"""
IBIS-AMI parameter parsing and configuration utilities.

Original author: David Banas <capn.freako@gmail.com>

Original date:   December 17, 2016

Copyright (c) 2019 David Banas; all rights reserved World wide.
"""
import logging
from pathlib import Path

from traits.api import Bool, Enum, HasTraits, Range, Trait
from traitsui.api import Group, Item, View
from traitsui.menu import ModalButtons

from pyibisami.ami.parameter import AMIParameter
from pyibisami.ami.parser import parse_ami_file


class AMIParamConfigurator(HasTraits):
    """
    Customizable IBIS-AMI model parameter configurator.

    This class can be configured to present a customized GUI to the user
    for configuring a particular IBIS-AMI model.

    The intended use model is as follows:

     1. Instantiate this class only once per IBIS-AMI model invocation.
        When instantiating, provide the unprocessed contents of the AMI
        file, as a single string. This class will take care of getting
        that string parsed properly, and report any errors or warnings
        it encounters, in its ``ami_parsing_errors`` property.

     2. When you want to let the user change the AMI parameter
        configuration, call the ``open_gui`` member function.
        (Or, just call the instance as if it were executable.)
        The instance will then present a GUI to the user,
        allowing him to modify the values of any *In* or *InOut* parameters.
        The resultant AMI parameter dictionary, suitable for passing
        into the ``ami_params`` parameter of the ``AMIModelInitializer``
        constructor, can be accessed, via the instance's
        ``input_ami_params`` property. The latest user selections will be
        remembered, as long as the instance remains in scope.

    The entire AMI parameter definition dictionary, which should *not* be
    passed to the ``AMIModelInitializer`` constructor, is available in the
    instance's ``ami_param_defs`` property.

    Any errors or warnings encountered while parsing are available, in
    the ``ami_parsing_errors`` property.

    """

    def __init__(self, ami_filepath: Path):
        """
        Args:
            ami_filepath: The filepath to the .ami file.
        """

        # Super-class initialization is ABSOLUTELY NECESSARY, in order
        # to get all the Traits/UI machinery setup correctly.
        super().__init__()
        self._log = logging.getLogger("pyibisami")

        # Parse the AMI file contents, storing any errors or warnings,
        # and customize the view accordingly.
        err_str, param_dict = parse_ami_file(ami_filepath)
        if not param_dict:
            self._log.error("Empty dictionary returned by parse_ami_file()!")
            self._log.error("Error message:\n%s", err_str)
            raise KeyError("Failed to parse AMI file; see console for more detail.")
        top_branch = list(param_dict.items())[0]
        param_dict = top_branch[1]
        if "Reserved_Parameters" not in param_dict:
            self._log.error("Error: %s\nParameters: %s", err_str, param_dict)
            raise KeyError("Unable to get 'Reserved_Parameters' from the parameter set.")
        if "Model_Specific" not in param_dict:
            self._log.error("Error: %s\nParameters: %s", err_str, param_dict)
            raise KeyError("Unable to get 'Model_Specific' from the parameter set.")
        pdict = param_dict["Reserved_Parameters"]
        pdict.update(param_dict["Model_Specific"])
        gui_items, new_traits = make_gui_items(
            # "Model Specific In/InOut Parameters", param_dict["Model_Specific"], first_call=True
            "Model In/InOut Parameters",
            pdict,
            first_call=True,
        )
        trait_names = []
        for trait in new_traits:
            self.add_trait(trait[0], trait[1])
            trait_names.append(trait[0])
        self._content = gui_items
        self._param_trait_names = trait_names
        self._root_name = top_branch[0]
        self._ami_parsing_errors = err_str
        self._content = gui_items
        self._param_dict = param_dict

    def __call__(self):
        self.open_gui()

    def open_gui(self):
        """Present a customized GUI to the user, for parameter customization."""
        self.edit_traits()

    def default_traits_view(self):
        view = View(
            resizable=False,
            buttons=ModalButtons,
            title="AMI Parameter Configurator",
            id="pyibisami.ami.param_config",
        )
        view.set_content(self._content)
        return view

    def fetch_param_val(self, branch_names):
        """Returns the value of the parameter found by traversing 'branch_names'
        or None if not found.
        Note: 'branch_names' should *not* begin with 'root_name'.
        """

        param_dict = self.ami_param_defs
        while branch_names:
            branch_name = branch_names.pop(0)
            if branch_name in param_dict:
                param_dict = param_dict[branch_name]
            else:
                return None
        if isinstance(param_dict, AMIParameter):
            return param_dict.pvalue
        return None

    def set_param_val(self, branch_names, new_val):
        """Sets the value of the parameter found by traversing 'branch_names'
        or raises an exception if not found.
        Note: 'branch_names' should *not* begin with 'root_name'.
        Note: Be careful! There is no checking done here!
        """

        param_dict = self.ami_param_defs
        while branch_names:
            branch_name = branch_names.pop(0)
            if branch_name in param_dict:
                param_dict = param_dict[branch_name]
            else:
                raise ValueError(
                    f"Failed parameter tree search looking for: {branch_name}; available keys: {param_dict.keys()}"
                )
        if isinstance(param_dict, AMIParameter):
            param_dict.pvalue = new_val
            try:
                eval(f"self.set({branch_name}_={new_val})")  # mapped trait; see below
            except Exception:
                eval(f"self.set({branch_name}={new_val})")  # pylint: disable=eval-used
        else:
            raise TypeError(f"{param_dict} is not of type: AMIParameter!")

    @property
    def ami_parsing_errors(self):
        """Any errors or warnings encountered, while parsing the AMI parameter definition file contents."""
        return self._ami_parsing_errors

    @property
    def ami_param_defs(self):
        """The entire AMI parameter definition dictionary.

        Should *not* be passed to ``AMIModelInitializer`` constructor!
        """
        return self._param_dict

    @property
    def input_ami_params(self):
        """The dictionary of *Model Specific* AMI parameters of type
        'In' or 'InOut', along with their user selected values.

        Should be passed to ``AMIModelInitializer`` constructor.
        """
        res = {}
        res["root_name"] = self._root_name
        params = self.ami_param_defs["Model_Specific"]
        for pname in params:
            res.update(self.input_ami_param(params, pname))
        return res

    def input_ami_param(self, params, pname):
        """Retrieve one AMI parameter, or dictionary of subparameters."""
        res = {}
        param = params[pname]
        if isinstance(param, AMIParameter):
            if pname in self._param_trait_names:  # If model specific and In or InOut...
                # See the docs on the *HasTraits* class, if this is confusing.
                try:  # Querry for a mapped trait, first, by trying to get '<trait_name>_'. (Note the underscore.)
                    res[pname] = self.get(pname + "_")[pname + "_"]
                except Exception:  # We have an ordinary (i.e. - not mapped) trait.
                    res[pname] = self.get(pname)[pname]
        elif isinstance(param, dict):  # We received a dictionary of subparameters, in 'param'.
            subs = {}
            for sname in param.keys():
                subs.update(self.input_ami_param(param, sname))
            res[pname] = subs
        return res


def make_gui_items(pname, param, first_call=False):
    """Builds list of GUI items from AMI parameter dictionary."""

    gui_items = []
    new_traits = []
    if isinstance(param, AMIParameter):
        pusage = param.pusage
        if pusage in ("In", "InOut"):
            if param.ptype == "Boolean":
                new_traits.append((pname, Bool(param.pvalue)))
                gui_items.append(Item(pname, tooltip=param.pdescription))
            else:
                pformat = param.pformat
                if pformat == "Range":
                    new_traits.append((pname, Range(param.pmin, param.pmax, param.pvalue)))
                    gui_items.append(Item(pname, tooltip=param.pdescription))
                elif pformat == "List":
                    list_tips = param.plist_tip
                    default = param.pdefault
                    if list_tips:
                        tmp_dict = {}
                        tmp_dict.update(list(zip(list_tips, param.pvalue)))
                        val = list(tmp_dict.keys())[0]
                        if default:
                            for tip, pvalue in tmp_dict.items():
                                if pvalue == default:
                                    val = tip
                                    break
                        new_traits.append((pname, Trait(val, tmp_dict)))
                    else:
                        val = param.pvalue[0]
                        if default:
                            val = default
                        new_traits.append((pname, Enum([val] + param.pvalue)))
                    gui_items.append(Item(pname, tooltip=param.pdescription))
                else:  # Value
                    new_traits.append((pname, param.pvalue))
                    gui_items.append(Item(pname, style="readonly", tooltip=param.pdescription))
    else:  # subparameter branch
        subparam_names = list(param.keys())
        subparam_names.sort()
        sub_items = []
        group_desc = ""

        # Build GUI items for this branch.
        for subparam_name in subparam_names:
            if subparam_name == "description":
                group_desc = param[subparam_name]
            else:
                tmp_items, tmp_traits = make_gui_items(subparam_name, param[subparam_name])
                sub_items.extend(tmp_items)
                new_traits.extend(tmp_traits)

        # Put all top-level non-grouped parameters in a single VGroup.
        top_lvl_params = []
        sub_params = []
        for item in sub_items:
            if isinstance(item, Item):
                top_lvl_params.append(item)
            else:
                sub_params.append(item)
        sub_items = [Group(top_lvl_params)] + sub_params

        # Make the top-level group an HGroup; all others VGroups (default).
        if first_call:
            gui_items.append(
                Group([Item(label=group_desc)] + sub_items, label=pname, show_border=True, orientation="horizontal")
            )
        else:
            gui_items.append(Group([Item(label=group_desc)] + sub_items, label=pname, show_border=True))

    return gui_items, new_traits

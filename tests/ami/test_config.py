import shutil
from pathlib import Path
from unittest.mock import patch

from pyibisami.tools import ami_generator


@patch.object(ami_generator, "date", autospec=True)
def test_ami_generator(mock_date, tmp_path):
    """Use example_tx.py and supporting cpp.em found under test/examples to generate a model."""

    mock_date.today.return_value = "2019-02-10"  # Mock the object data so that we can test it.

    # Copy the examples to a temproray path.
    FILES = ["example_tx.py", "example_tx.cpp.em"]
    examples_folder = Path(__file__).parents[1].joinpath("examples")
    for file in FILES:
        shutil.copy(examples_folder.joinpath(file), tmp_path.joinpath(file))

    ami_generator.ami_generator(py_file=tmp_path.joinpath("example_tx.py"))

    with open(tmp_path.joinpath("example_tx.ami"), encoding="UTF-8") as ami_file:
        ami = ami_file.read()
        assert (
            ami
            == r"""(example_tx

    (Description "Example Tx model from ibisami package.")

    (Reserved_Parameters
         (AMI_Version
             (Usage Info )
             (Type String )
             (Value "5.1" )
             (Description "Version of IBIS standard we comply with." )
         )
         (Init_Returns_Impulse
             (Usage Info )
             (Type Boolean )
             (Value True )
             (Description "In fact, this model is, currently, Init-only." )
         )
         (GetWave_Exists
             (Usage Info )
             (Type Boolean )
             (Value True )
             (Description "This model is dual-mode, with GetWave() mimicking Init()." )
         )
    )
    (Model_Specific
         (tx_tap_units
             (Usage In )
             (Type Integer )
             (Range 27 6 27 )
             (Description "Total current available to FIR filter." )
         )
         (tx_tap_np1
             (Usage In )
             (Type Integer )
             (Range 0 0 10 )
             (Description "First (and only) pre-tap." )
         )
         (tx_tap_nm1
             (Usage In )
             (Type Integer )
             (Range 0 0 10 )
             (Description "First post-tap." )
         )
         (tx_tap_nm2
             (Usage In )
             (Type Integer )
             (Range 0 0 10 )
             (Description "Second post-tap." )
         )
    )

)
"""
        )

    with open(tmp_path.joinpath("example_tx.ibs"), encoding="UTF-8") as ibis_file:
        ibis = ibis_file.read()
        assert (
            r"""[IBIS Ver]   5.1



[File Name]  example_tx.ibs
[File Rev]   v0.1

[Date]       2019-02-10

[Source]     ibisami, a public domain IBIS-AMI model creation infrastructure

[Disclaimer]
THIS MODEL IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS MODEL, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

[Notes]
This IBIS file was generated, using the template file,
"example_tx.ibs.em", from ibisami, a public domain IBIS-AMI model
creation infrastructure. To learn more, visit:

https://github.com/capn-freako/ibisami/wiki

[Copyright]    Copyright (c) 2016 David Banas; all rights reserved World wide.
[Component]    Example_Tx
[Manufacturer] (n/a)

[Package]

R_pkg     0.10     0.00     0.50
L_pkg    10.00n    0.10n   50.00n
C_pkg     1.00p    0.01p    5.00p


[Pin]  signal_name        model_name            R_pin  L_pin  C_pin
1p     Tx_1_P             example_tx
1n     Tx_1_N             example_tx
2p     Tx_2_P             example_tx
2n     Tx_2_N             example_tx
3p     Tx_3_P             example_tx
3n     Tx_3_N             example_tx

[Diff_Pin] inv_pin vdiff tdelay_typ tdelay_min tdelay_max
1p           1n     0.1V     NA         NA         NA
2p           2n     0.1V     NA         NA         NA
3p           3n     0.1V     NA         NA         NA

[Model]   example_tx
Model_type   Output

C_comp     1.00p    0.01p    5.00p
Cref  = 0
Vref  = 0.5
Vmeas = 0.5
Rref  = 50


[Algorithmic Model]
Executable linux_gcc4.1.2_32          example_tx_x86.so         example_tx.ami
Executable linux_gcc4.1.2_64          example_tx_x86_amd64.so   example_tx.ami
Executable Windows_VisualStudio_32    example_tx_x86.dll        example_tx.ami
Executable Windows_VisualStudio_64    example_tx_x86_amd64.dll  example_tx.ami
[End Algorithmic Model]

[Temperature_Range]     25.0      0.0    100.0
[Voltage_Range]         1.80     1.62     1.98
"""
            in ibis
        )

    with open(tmp_path.joinpath("example_tx.cpp"), encoding="UTF-8") as cpp_file:
        cpp = cpp_file.read()
        assert (
            cpp
            == r"""/** \file example_tx.cpp
 *  \brief Example of using ibisami to build a Tx model.
 *
 * Original author: David Banas <br>
 * Original date:   May 8, 2015
 * Initial conversion to EmPy template format: Feb 25, 2016
 *
 * Copyright (c) 2015 David Banas; all rights reserved World wide.
 */

#define TAP_SCALE 0.0407

#include <string>
#include <vector>
#include "include/ami_tx.h"

/// An example device specific Tx model implementation.
class MyTx : public AmiTx {
    typedef AmiTx inherited;

 public:
    MyTx() {}
    ~MyTx() {}
    void init(double *impulse_matrix, const long number_of_rows,
            const long aggressors, const double sample_interval,
            const double bit_time, const std::string& AMI_parameters_in) override {

        // Let our base class do its thing.
        inherited::init(impulse_matrix, number_of_rows, aggressors,
            sample_interval, bit_time, AMI_parameters_in);

        // Grab our parameters and configure things accordingly.
        std::vector<std::string> node_names; node_names.clear();
        std::ostringstream msg;

        msg << "Initializing Tx...\n";

        int taps[4];
        int tx_tap_units ;
        node_names.push_back("tx_tap_units");
        tx_tap_units = get_param_int(node_names, 27 );
        node_names.pop_back();
        int tx_tap_np1 ;
        node_names.push_back("tx_tap_np1");
        tx_tap_np1 = get_param_int(node_names, 0 );
        taps[0] = tx_tap_np1;
        node_names.pop_back();
        int tx_tap_nm1 ;
        node_names.push_back("tx_tap_nm1");
        tx_tap_nm1 = get_param_int(node_names, 0 );
        taps[2] = tx_tap_nm1;
        node_names.pop_back();
        int tx_tap_nm2 ;
        node_names.push_back("tx_tap_nm2");
        tx_tap_nm2 = get_param_int(node_names, 0 );
        taps[3] = tx_tap_nm2;
        node_names.pop_back();

        taps[1] = tx_tap_units - (taps[0] + taps[2] + taps[3]);
        if ( (tx_tap_units - 2 * (taps[0] + taps[2] + taps[3])) < 6 )
            msg << "WARNING: Illegal Tx pre-emphasis tap configuration!\n";

        // Fill in params_.
        std::ostringstream params;
        params << "(example_tx";
        params << " (tx_tap_units " << tx_tap_units << ")";
        params << " (taps[0] " << taps[0] << ")";
        params << " (taps[1] " << taps[1] << ")";
        params << " (taps[2] " << taps[2] << ")";
        params << " (taps[3] " << taps[3] << ")";

        tap_weights_.clear();
        int samples_per_bit = int(bit_time / sample_interval);
        int tap_signs[] = {-1, 1, -1, -1};
        have_preemph_ = true;
        for (auto i = 0; i <= 3; i++) {
            tap_weights_.push_back(taps[i] * TAP_SCALE * tap_signs[i]);
            params << " (tap_weights_[" << i << "] " << tap_weights_.back() << ")";
            for (auto j = 1; j < samples_per_bit; j++)
                tap_weights_.push_back(0.0);
        }
        param_str_ = params.str() + "\n";
        msg_ = msg.str() + "\n";
    }
} my_tx;

AMIModel *ami_model = &my_tx;  ///< The pointer required by the API implementation.

"""
        )

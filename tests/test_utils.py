from pyibisami.utils import loadWave


def test_loadWave(tmp_path):
    """Simple test case to verify pytest and tox is up and working."""
    waveform = tmp_path.joinpath("waveform.txt")
    with open(waveform, "w") as test_file:
        test_file.write("Time Voltage\n")
        test_file.write("0.00 .000\n")
        test_file.write("0.01 .001\n")
        test_file.write("0.02 .002\n")
        test_file.write("0.03 .003\n")
        test_file.write("0.04 .004\n")

    wave = loadWave(waveform)
    assert len(wave[0]) == len(wave[1])
    assert len(wave[0]) == 5

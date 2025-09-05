from larixite import get_amcsd
from larixite.utils import get_logger
from larixite.struct import get_structure
from larixite.fdmnes import FdmnesXasInput

logger = get_logger("larixite.test")


def test_fdmnes():
    db = get_amcsd()
    cifids = {
        4438: ("S", "Fe"),
        4820: ("Ti", "Fe"),
        143: ("Fe", "O"),
        2400: ("Fe", "O"),
        2762: ("Fe", "O"),
    }

    for cifid, atoms in cifids.items():
        cif = db.get_cif(cifid)
        outfile = cif.write_cif(verbose=True)
        for abs in atoms:
            logger.info(f"[{cif.label}] {abs}")
            sg = get_structure(outfile, abs)
            f = FdmnesXasInput(sg, absorber=abs)
            text = f.get_input()
            assert len(text) > 700  # TODO: find a better test
            #: test the inputs writes correctly to disk into a temporary directory
            outdir = f.write_input()
            assert outdir.exists()


if __name__ == "__main__":
    test_fdmnes()

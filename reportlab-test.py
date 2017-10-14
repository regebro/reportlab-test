import glob
import os
import pkg_resources
import shutil
from PIL import Image
from z3c.rml import rml2pdf


def gs_command(path):
    return ' '.join(('gs', '-q', '-sNOPAUSE', '-sDEVICE=png256',
                     '-sOutputFile=%s[Page-%%d].png' % path[:-4],
                     path, '-c', 'quit'))


def get_image_data(filename):
    with open(filename, 'rb') as imgfile:
        img = Image.open(filename).getdata()
        return [img[i] for i in range(len(img))]


def main(infilename):
    # First print out some environment information
    outdir = os.path.join(os.path.abspath(os.path.curdir), 'output')
    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    # First we do this test ten times, and gather
    testdata = {}
    testfilenames = {}
    different_files = []
    for i in range(10):
        pdf_filename = os.path.join(outdir, 'test-%02i.pdf' % i)
        rml2pdf.go(infilename, pdf_filename)

        # Remove old png files.
        for filename in glob.glob(os.path.join(outdir, 'test-%02i*.png' % i)):
            os.unlink(filename)

        # Now convert this to PNG, and save that data
        os.system(gs_command(pdf_filename))

        # Load the images generated
        png_files = glob.glob(os.path.join(outdir, 'test-%02i*.png' % i))
        testdata[i] = {}
        testfilenames[i] = {}
        for k, filename in enumerate(sorted(png_files)):
            testdata[i][k] = get_image_data(filename)
            testfilenames[i][k] = filename

        # Then convert it 2 more times, for a total of 3, and check that the
        # output is the same every time. This is to test that Ghostscript
        # will create the same PNG every time from the same source.
        for j in range(2):
            # Convert again
            os.system(gs_command(pdf_filename))

            png_files = glob.glob(os.path.join(outdir, 'test-%02i*.png' % i))
            for k, filename in enumerate(sorted(png_files)):
                testimage = get_image_data(filename)
                # This whole test is based on the assumption that ghostscrip
                # creates the same PNG on multiple runs, so if this is untrue
                # we can just as well just fail.
                assert testdata[i][k] == testimage

        # Lastly check that each PDF conversion is the same, pixel by pixel
        for k, filename in enumerate(sorted(png_files)):
            # Sanity check
            assert filename == testfilenames[i][k]

            # Check that the data is the same
            if testdata[i][k] != testdata[0][k]:
                different_files.append((filename, testfilenames[0][k]))

    print("Result\n======")
    print("%s files out of 27 was different from the first run:" % len(different_files))
    for files in different_files:
        print("%s was different from %s" % files)

    if different_files:
        raise RuntimeError("Found a difference!")


if __name__ == "__main__":
    print("reportlab-test\n==============\n")
    print("reportlab:")
    print(pkg_resources.get_distribution("reportlab").version)
    print("ghostscript:")
    result = os.system("gs --version")
    if result != 0:
        raise RuntimeError("Could not launch gs, make sure Ghostscript is installed")


    rmlfiles = glob.glob('/home/projects/Shoobx/z3c.rml/src/z3c/rml/tests/input/*.rml')
    for c, filename in enumerate(sorted(rmlfiles)):
        print("===============")
        print(filename)
        print("%s of %s" % (c, len(rmlfiles)))
        try:
            main(filename)
        except ImportError:
            print("failed")
        print("===============")

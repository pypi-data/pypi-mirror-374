# Pyscan

Create a PDF file from a list of images using [OpenCV](https://opencv.org/).

---

## Usage

    $ pydfscanner "image_paths" -o "output_pdf_path"

If the document was not correctly scanned there is a way to find where the
process failed. Just run:

    $ pydfscanner --debug "image_paths" -o "output_pdf_path"

Along the final (although incorrect) scanned document there will be an
additional file with the original image with the detected document's corners and
edges -- red dots and lines -- and all detected edges in the image -- blue lines
--. 

Run `pydfscanner -h` for additional flags and help.

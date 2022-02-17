from openpyxl import Workbook


def exportToExcel(file_path, rows):
    """
        Writes data to an excel file.
        file_path: Path object designating the worksheet in which
            the data will be written. Will create the worksheet
            if it does not exist, and overwrite the data otherwise.
        rows: 2-dimensional indexed collection (such as a list of lists,
            or tuple of tuples). Each element in the outer collection will
            be read as a row to be written to the worksheet.
    """

    # convert Path to string
    file_path = str(file_path)

    # initialize workbook
    workb = Workbook()
    works = workb.active

    # write rows
    for row in rows:
        works.append(row)

    # save workbook
    workb.save(filename=file_path)

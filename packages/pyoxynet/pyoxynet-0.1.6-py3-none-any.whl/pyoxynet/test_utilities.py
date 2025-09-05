from testing import Test

t = Test('/Users/andreazignoli/Downloads/Regnanti_Matteo_FAT_MAX')
t.clear_file_name()
t.set_data_extension('.xlsx')
t.infer_metabolimeter()
t.load_file()
t.create_data_frame()
t.create_raw_data_frame()

here=0
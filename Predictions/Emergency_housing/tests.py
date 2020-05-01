import unittest

import numpy as np
import pandas as pd

from cobratools import Analysis


class TestDataFuncs(unittest.TestCase):

    def test_get_data_chunck(self):
        
        # Test df
        df = pd.DataFrame({'A':[1, 2, 3, 4], 'B':[4, 5, 5, 7]})

        # Instanciate obj with test df
        obj_df = Analysis(df)
        
        # Define cases
        cases = [{'chunck_size': 2,
                    'iloc_start': 1},
                 {'chunck_size': 2,
                    'iloc_start': 2},
                 {'chunck_size': 2,
                    'iloc_start': 3}]

        results = [{'iloc_start': 1,
                      'iloc_end': 3},
                   {'iloc_start': 2,
                      'iloc_end': 4},
                  # test out-of bound
                   {'iloc_start': 3,
                      'iloc_end': 4}]

        # Apply and check each case
        for c, r in zip(cases, results):
            chunck_obtained = obj_df.get_data_chunck(iloc_start=c['iloc_start'],
                                                     chunck_size=c['chunck_size'])

            # Expected output
            chunck_expected = df.iloc[r['iloc_start']: r['iloc_end']]

            # Control expected == obtained
            bool_result = chunck_expected.equals(chunck_obtained)

            # Assert
            self.assertTrue(bool_result)



if __name__=='__main__':
    
    unittest.main()

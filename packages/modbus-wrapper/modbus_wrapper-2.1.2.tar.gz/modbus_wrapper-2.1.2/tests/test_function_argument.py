from modbus_wrapper.function_argument import FunctionArgument

class TestFunctionArgument:
    
    
    class TestCalculateReadSize:
        
        def test_standard(self):
            addresses = [10,2,3,5,1]
            result = FunctionArgument._calculate_read_size(addresses)
            assert result[0] == {'starting_address' : 1,
                                 'size' : 1,
                                 'addresses': [1]}
            assert result[1] == {'starting_address' : 2,
                                 'size' : 1,
                                 'addresses': [2]}
            assert result[2] == {'starting_address' : 3,
                                 'size' : 1,
                                 'addresses': [3]}
            assert result[3] == {'starting_address' : 5,
                                 'size' : 1,
                                 'addresses': [5]}
            assert result[4] == {'starting_address' : 10,
                                 'size' : 1,
                                 'addresses': [10]}
            assert len(result) == 5

            
        def test_duplicates(self):
            addresses = [10,2,3,5,1,10]
            result = FunctionArgument._calculate_read_size(addresses)
            assert result[0] == {'starting_address' : 1,
                                 'size' : 1,
                                 'addresses': [1]}
            assert result[1] == {'starting_address' : 2,
                                 'size' : 1,
                                 'addresses': [2]}
            assert result[2] == {'starting_address' : 3,
                                 'size' : 1,
                                 'addresses': [3]}
            assert result[3] == {'starting_address' : 5,
                                 'size' : 1,
                                 'addresses': [5]}
            assert result[4] == {'starting_address' : 10,
                                 'size' : 1,
                                 'addresses': [10,10]}
            
            
        def test_max_read_size(self):
            addresses = [10,2,3,5,1]
            max_read_size = 10
            result = FunctionArgument._calculate_read_size(addresses, max_read_size)
            assert result[0] == {'starting_address' : 1,
                                 'size' : 3,
                                 'addresses': [1,2,3]}
            assert result[1] == {'starting_address' : 5,
                                 'size' : 1,
                                 'addresses': [5]}
            assert result[2] == {'starting_address' : 10,
                                 'size' : 1,
                                 'addresses': [10]}
            assert len(result) == 3
            
        def test_read_mask_2(self):
            addresses = [10,2,3,5,1]
            max_read_size = 10
            read_mask = 2
            result = FunctionArgument._calculate_read_size(addresses, max_read_size, read_mask)
            assert result[0] == {'starting_address' : 1,
                                 'size' : 5,
                                 'addresses': [1,2,3,5]}
            assert result[1] == {'starting_address' : 10,
                                 'size' : 1,
                                 'addresses': [10]}
            assert len(result) == 2
            
        def test_read_mask_6(self):
            addresses = [10,2,3,5,1]
            max_read_size = 10
            read_mask = 6
            result = FunctionArgument._calculate_read_size(addresses, max_read_size, read_mask)
            assert result[0] == {'starting_address' : 1,
                                 'size' : 10,
                                 'addresses': [1,2,3,5,10]}
            assert len(result) == 1
            
        def test_read_mask_lt_max_read_size(self):
            addresses = [10,2,3,5,1]
            max_read_size = 3
            read_mask = 15
            result = FunctionArgument._calculate_read_size(addresses, max_read_size, read_mask)
            assert result[0] == {'starting_address' : 1,
                                 'size' : 3,
                                 'addresses': [1,2,3]}
            assert result[1] == {'starting_address' : 5,
                                 'size' : 1,
                                 'addresses': [5]}
            assert result[2] == {'starting_address' : 10,
                                 'size' : 1,
                                 'addresses': [10]}
            assert len(result) == 3
            
            
        def test_read_mask_max_read_size(self):
            addresses = [100,300,200,500,502]
            max_read_size = 201
            read_mask = 200
            result = FunctionArgument._calculate_read_size(addresses, max_read_size, read_mask)
            assert result[0] == {'starting_address' : 100,
                                 'size' : 201,
                                 'addresses': [100,200,300]}
            assert result[1] == {'starting_address' : 500,
                                 'size' : 3,
                                 'addresses': [500,502]}
            assert len(result) == 2
            
      

            


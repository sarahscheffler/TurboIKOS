from Value import Value 

class gate:
    # input: 2 inputs, 3 triples/ 0's
    def __init__(self, input1, input2, output, n_parties, *, wire = None, operation=None):
        self.operation = operation
        self.n_parties = n_parties
        self.w = wire
        self.x = input1
        self.y = input2
        self.z = output
    
    def __repr__(self):
        return 'operation:' + str(self.operation) + ' x:' + str(self.x) + ' y:' + str(self.y) + ' z:' + str(self.z)

    # Assigns v values z = x + y for each party
    # Assign e value on output wire
    def add(self):
        z_v_arr = [None]*self.n_parties
        # calculate z_v
        for i in range(self.n_parties):
            x_v = self.w.v(self.x)[i]
            y_v = self.w.v(self.y)[i]
            z_v = x_v + y_v
            z_v_arr[i] = z_v
        # set z_v
        self.w.set_v(self.z, z_v_arr)
        # calculate z_e
        x_e = self.w.e(self.x)
        y_e = self.w.e(self.y)
        if not x_e:
            x_v = sum(self.w.v(self.x))
            x_lam = sum(self.w.lambda_val(self.x)) 
            x_e = (x_v + x_lam)
            self.w.set_e(self.x, x_e)
        if not y_e:
            y_v = sum(self.w.v(self.y))
            y_lam = sum(self.w.lambda_val(self.y))
            y_e = (y_v + y_lam)  
            self.w.set_e(self.y, y_e)
        z_e = x_e + y_e
        # set z_e
        self.w.set_e(self.z, z_e)

    # Assigns v values  z = x*y for each party
    # assign e value on output wire
    # return e share for broadcast
    def mult(self, mult_count):
        z_v_arr = [None]*self.n_parties 
        # calculate z_vi
        x_e = self.w.e(self.x)
        y_e = self.w.e(self.y)
        if not x_e:
            x_v = sum(self.w.v(self.x))
            x_lam = sum(self.w.lambda_val(self.x))
            x_e = (x_v + x_lam)
            self.w.set_e(self.x, x_e)
        if not y_e:
            y_v = sum(self.w.v(self.y))
            y_lam = sum(self.w.lambda_val(self.y))
            y_e = (y_v + y_lam)
            self.w.set_e(self.y, y_e)
        #Calculate z_e
        z_v = sum(self.w.v(self.x)) * sum(self.w.v(self.y))
        z_e = z_v + sum(self.w.lambda_val(self.z))
        # calculate and set z_eh
        z_eh = sum(self.w.lambda_val(self.x)) * sum(self.w.lam_hat(self.y)[str(mult_count)]) + \
            sum(self.w.lam_hat(self.z)[str(mult_count)])
        self.w.set_e_hat(self.z, z_eh)
        for i in range(self.n_parties):
            # calculate z_vi
            if i == 0:
                z_v_share = z_e - self.w.lambda_val(self.z)[i]
            else:
                z_v_share = Value(0) - self.w.lambda_val(self.z)[i]
            z_v_arr[i] = z_v_share 
     
          
        self.w.set_v(self.z, z_v_arr)
        # calculate and set z_e
        z_e = sum(self.w.v(self.z)) + sum(self.w.lambda_val(self.z))
        self.w.set_e(self.z, z_e)
    
    def inv(self):
        self.w.set_v(self.z, [None]* self.n_parties)
        for i in range(self.n_parties):
            if i == 0:
                self.w.v(self.z)[i] = self.w.v(self.x)[i] + Value(1)
            else:
                self.w.v(self.z)[i] = self.w.v(self.x)[i]
        self.w.set_e(self.z, self.w.e(self.x))

    # performs Scalar mult (new code)
    def sca(self):
        z_v_arr = [None]*self.n_parties
        const = self.y
        # calculate z_v
        for i in range(self.n_parties):
            x_v = self.w.v(self.x)[i]
            z_v = x_v * const
            z_v_arr[i] = z_v
        # set z_v
        self.w.set_v(self.z, z_v_arr)
        # calculate z_e
        x_e = self.w.e(self.x)
        if not x_e:
            x_v = sum(self.w.v(self.x))
            x_lam = sum(self.w.lambda_val(self.x)) 
            x_e = (x_v + x_lam)
            self.w.set_e(self.x, x_e)
        
        z_e = sum(self.w.v(self.z)) + sum(self.w.lambda_val(self.z))
        # set z_e
        self.w.set_e(self.z, z_e)
       

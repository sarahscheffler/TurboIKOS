from secrets import token_bytes

def verifier():
    """
    #circuit is known or sent beforehand
    epsilon = token_bytes(16)
    epsilon_hat = token_bytes(16)
    # send to prover epsilon and epsilon_hat
    # open up c and check that it equals to zero
    """

    #assume non interactivity 

    #receiving commitments from Prover which consist of lambda shares, beaver triple shares, input shares, broadcast

    #parse circuit with circuit.parse 

    #recompute circuit
    """"
    # calculate circuit 
    # keep track of output value from each gate, zeta share alpha share, and c value 
    """"

    #check broadcast channel matches recomputation
    """
    # check broadcast channel with recomputation from recomputing circuit 
    # abort if any broadcast does not match 
    """

    #check zetas 
    """
    # check zeta with recomputation 
    # assert zeta == 0, else abort 
    # [zeta] = epsilon*{v_z}-{lambda_c}+alpha*{lambda_y}+{e_y}*{lambda_x}-{alpha}*{e_y}
    """    

    #check alphas 
    """
    # [alpha] = epsilon*[r_y] + (hat{epsilon})*[hat{r_y}]
        # NOTE: [alpha] will denote shares of whatever is inside the brackets
    # get shares of alpha (alpha_broadcast, array) from circuit.compute_ouput 
    # or generate alphas completely again and double check that they match with Prover.py commitments? 
    """
    
    #check output == 1
    """
    # calculate c for every mult gate 
    # add up all the c values and assert that == 1
    """
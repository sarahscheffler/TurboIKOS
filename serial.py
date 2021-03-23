
import pickle
from Value import Value
import gmpy2

#serializing using pickle for Value objects

def serial(info): 
    for i in range(len(info)):
        if type(info[i]) == list:
            for j in range(len(info[i])):
                temp = gmpy2.to_binary(info[i][j].value)
                info[i][j] = temp
        else: 
            temp = gmpy2.to_binary(info[i].value)
            info[i] = temp
    return pickle.dumps(info)

def deserial(info): 
    info = pickle.loads(info)
    for i in range(len(info)):
        if type(info[i]) == list:
            for j in range(len(info[i])):
                temp = gmpy2.from_binary(info[i][j])
                info[i][j] = Value(temp)
        else:
            print(info[i])
            temp = gmpy2.from_binary(info[i])
            info[i] = Value(temp)
    return info
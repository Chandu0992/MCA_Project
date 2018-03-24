from flask import Flask, redirect, request
from itertools import product as d
import re
import json

n=range
app = Flask(__name__)
@app.route('/genPlayfair')
def genPlayfair():
    c_key = request.args.get('cipher_key')
    result = table_gen(c_key)
    return json.dumps(list(map(ord,result)))

def table_gen(c_key):
    key_AtoZ = list(map(chr,list(range(65,91))))
    key_atoz = list(map(chr,list(range(97,123))))
    key_0to9 = list(map(str,range(0,10)))
    brackets_list = ['(',')','[',']','{','}','`','~','!','@','#','$','%','^','&','*','-','+','/','.','<','>','?','|','_']
    sub_list = key_AtoZ+key_atoz+key_0to9+brackets_list
    key_list=list(''.join(sorted(set(c_key), key=c_key.index)))
    main_list1 = key_list
    for char in sub_list:
        if char not in key_list:
            main_list1.append(char)
    sub_list1 = list(range(0,256))
    for i in range(0,256):
        if chr(i) in main_list1:
            pass
        else:
            main_list1.append(chr(i))
    return main_list1

@app.route('/genComparisonMac')
def genComparisonMac():
    msg = request.args.get('sMsg')
    skey2 = request.args.get('skey2')
    smac = request.args.get('smac')
    msgInv = bytes(msg,"ascii")
    binary_msg_Inv =''.join(["{0:08b}".format(x)for x in msgInv])

    if(len(binary_msg_Inv)<=len(skey2)):
        length_mac = len(skey2)-len(binary_msg_Inv)
        binary_msg_Inv = '0'*length_mac + binary_msg_Inv

        comp_lement = binary_msg_Inv
        complemented_res = []
        for i in range(0,len(comp_lement)):
            if comp_lement[i] == '1':
                complemented_res.append('0')
            else:
                complemented_res.append('1')
        complemented_res = ''.join(map(str,complemented_res))

        InvMsg = complemented_res
        rmac = ''
        for i in range(0,len(skey2)):
            rmac = rmac + str(ord(skey2[i])^ord(InvMsg[i]))

        if(smac == rmac):
            return json.dumps({'rmac':rmac,'status_msg':"Message is Not Altered"})
        else:
            return json.dumps({'rmac':rmac,'status_msg':"Message is Altered"})

    else:
        return json.dumps({'rmac':"Your Message Length is Grater Than Key2",'status_msg':"Your Message is Modified and Mac cant be Generated"})
          

    
@app.route('/genCipher')
def genCipher():
    p=request.args.get('txt_msg')
    c_key = request.args.get('c_key')
    main_list1 = table_gen(c_key)
    m=[main_list1[i:i+16] for i in n(0,len(main_list1),16)]
    e={r[i]+r[j]:r[(i+1)%16]+r[(j+1)%16] for r in m for i,j in d(n(16),repeat=2) if i!=j}
    e.update({m[i1][j1]+m[i2][j2]:m[i1][j2]+m[i2][j1] for i1,j1,i2,j2 in d(n(16),repeat=4) if i1!=i2 and j1!=j2})
    l=re.findall(r'(.)(?:(?!\1)(.))?',''.join([_ for _ in p if _ in main_list1]))
    cipher_text = ''.join(e[a+(b if b else 'X')] for a,b in l)
    key1 = c_key
    mesg = p
    o_bits = '00000000'
    k_bytes=bytes(cipher_text,"ascii")
    binary_cipher = ''.join(["{0:08b}".format(x)for x in k_bytes])
    return json.dumps({'cipher_text':cipher_text,'binary_text':binary_cipher})
@app.route('/genMac')
def genMac():
    ent1 = request.args.get('ent1')
    key1 = request.args.get('key1')
    c_key = key1
    mesg = request.args.get('mesg')
    p=mesg
    o_bits = '00000000'

    k_bytes=bytes(ent1,"ascii")
    k_key=bytes(key1,"ascii")
    k_mesg=bytes(mesg,"ascii")
    binary_cipher = ''.join(["{0:08b}".format(x)for x in k_bytes])
    binary_key=''.join(["{0:08b}".format(x)for x in k_key])
    binary_msg=''.join(["{0:08b}".format(x)for x in k_mesg])
    
    if(len(c_key)< len(p)):
        length_key = len(mesg)-len(key1)
        binary_key = o_bits*length_key + binary_key
    else:
        length_key = len(key1) - len(mesg)
        if(len(p)%2==1):
            length_key = length_key -1
        binary_cipher = o_bits*length_key + binary_cipher

    key2=''
    for i in range(0,len(binary_cipher)):
        key2 = key2 + str(ord(binary_cipher[i])^ord(binary_key[i]))
        
    if(len(key2)<len(binary_msg)):
        length_mac = len(binary_msg)-len(key2)
        key2= '0'*length_mac + key2
    else:
        length_mac = len(key2)-len(binary_msg)
        binary_msg = '0'*length_mac + binary_msg

    comp_lement = binary_msg
    complemented_res = []
    for i in range(0,len(comp_lement)):
        if comp_lement[i] == '1':
            complemented_res.append('0')
        else:
            complemented_res.append('1')
    complemented_res = ''.join(map(str,complemented_res))

    InvMsg = complemented_res
    mac = ''
    for i in range(0,len(key2)):
        mac = mac + str(ord(key2[i])^ord(InvMsg[i]))
    return json.dumps({'key2':key2,'InvMsg':InvMsg,'mac':mac})


   
if __name__ == '__main__':
    app.run(debug=True)

from types import NoneType
from PIL import Image
from random import seed,randint
from moviepy.editor import VideoFileClip
from pathlib import Path, PurePath
import os
from math import ceil, floor
import sys
import shutil
import re
import argparse
from inspect import getframeinfo, currentframe

def get_msg_from_video(filename,seed_value, evenness,ratio,mult_coef):
    scriptname = getframeinfo(currentframe()).filename
    cwd_path = os.path.dirname(os.path.abspath(scriptname))
    
    Path(os.fspath(PurePath(cwd_path,'frames_folder3'))).mkdir()
    
    clip = VideoFileClip(filename)
    print(f'get msg duration = {clip.duration}')
    print(f'fps = {clip.fps}')
        
    clip.write_images_sequence(os.fspath(PurePath(cwd_path,'frames_folder3','frame%09d.png')), logger='bar')
    directory=sorted(os.listdir(os.fspath(PurePath(cwd_path,'frames_folder3'))))
    fnames = []
    for fname in directory:
        if int(ord(fname[-5]) - ord('0')) % 2 == evenness:
            fnames.append(fname)
    width, height = clip.size
    px_num = width * height
 
    maxlen = floor((len(fnames)*3*px_num/(ratio * mult_coef))/8)
    raw_msg = bytearray(maxlen * mult_coef)
 
    offset = 0
    print(f'unique message length = {maxlen} symbols')
    bits_per_frame = float(mult_coef * maxlen * 8)/float(len(fnames))
    print(f'secret bits per frame = {bits_per_frame}, rounded to {ceil(bits_per_frame)}')
    bits_per_frame = ceil(bits_per_frame)
    seed(seed_value)
    
    for fname in fnames:
        if offset>=0:
            ret = get_bytes_from_img(os.fspath(PurePath(cwd_path,'frames_folder3', fname)), raw_msg, bits_per_frame, offset)
            if ret == 0:
                offset+=bits_per_frame
    
    print()
    print()
    print(f'Raw recovered message(multiplied): {str(raw_msg)}')
    print('Trying to get original message:')
    print(f'Supposed message length = {maxlen}')
    result_msg = recover_msg(maxlen,raw_msg,mult_coef)
    msg_list = []
    msg_list.extend(map(chr,result_msg))
    print(f'MESSAGE = {str(msg_list)}')
    
    return 0   

def recover_msg(orig_msg_len,raw_msg,mult_coef):
    result_msg = bytearray(orig_msg_len)
    for bit_index in range(orig_msg_len*8):
        equilibrium = 0
        index_in_byte = (bit_index % 8)
        byte_index = (bit_index)//8
        for multi_frame_index in range(mult_coef):
            index_in_byte = ((bit_index)%8)
            
            byte_index = multi_frame_index*orig_msg_len + bit_index//8
            #print(f'byte = {bin(raw_msg[byte_index])}')
            bit_value = bool(raw_msg[byte_index] % (2**((7-index_in_byte)+1)) - raw_msg[byte_index] % (2**(7-index_in_byte)))
            if bit_value:
                equilibrium += 1
            else:
                equilibrium -= 1
        result_msg[bit_index//8] <<= 1
        #print(f'equilibrium = {equilibrium}')
        if equilibrium > 0:
            result_msg[bit_index//8] += 1
            #print(f'bit[{bit_index}] = 1')
        #else:
            #print(f'bit[{bit_index}] = 0')
    return result_msg

def get_bytes_from_img(frame_path, msg_bytes, bits_number, offset):
    print(frame_path)
    frame = Image.open(frame_path).convert('RGBA')
    width, height = frame.size
    util_pxs  = []
    colour_flag = 0

    for bit_index_in_msg in range(bits_number):
        if (offset+bit_index_in_msg == (len(msg_bytes)*8)):
            return -1
        index_in_byte = ((offset + bit_index_in_msg)%8)
        if(index_in_byte == 0):
            print('New byte:')
        byte_index = (offset + bit_index_in_msg)//8
        #msg_bit = bool(msg_bytes[byte_index] % (2**(index_in_byte+1)) - msg_bytes[byte_index] % (2**index_in_byte))
        #print()
        #print(f'currently enbedded bit is {int(msg_bit)}')
        if colour_flag == 0:
            flag = 1
            while flag:
                px_x = randint(0,width - 1)
                px_y = randint(0,height - 1)
                if len(util_pxs):
                    for util_px_index in range(len(util_pxs)):
                        #print(f'index = {util_px_index}')
                        #print(f'util_px = {util_pxs[util_px_index]}')
                        if (util_pxs[util_px_index] == px_x and util_pxs[util_px_index] == px_y):
                            break
                        elif util_px_index == (len(util_pxs)-1):
                            flag = 0
                            break
                else:
                    break
            util_pxs.append([px_x,px_y])
            r, g, b, a = frame.getpixel((px_x, px_y))
            
            #print(f'modified r = {bin(r)}')
            recovered_bit =  r % 2
            print(f'{bit_index_in_msg})  recovered {recovered_bit} in ({px_x}, {px_y}): R({r})')
            #print(f'index in byte = {index_in_byte}')
            msg_bytes[byte_index] <<= 1
            msg_bytes[byte_index] += recovered_bit
            colour_flag = 1
            #print(f'red or blue is now {colour_flag}')
        elif colour_flag == 1:
            #print(f'modified b = {bin(b)}')
            recovered_bit = b % 2
            print(f'{bit_index_in_msg})  recovered {recovered_bit} in ({px_x}, {px_y}): B({b})')
            #print(f'index in byte = {index_in_byte}')
            msg_bytes[byte_index] <<= 1
            msg_bytes[byte_index] += recovered_bit
            colour_flag = 2
        elif colour_flag == 2:
            recovered_bit = g % 2
            print(f'{bit_index_in_msg})  recovered {recovered_bit} in ({px_x}, {px_y}): G({g})')
            #print(f'index in byte = {index_in_byte}')
            msg_bytes[byte_index] <<= 1
            msg_bytes[byte_index] += recovered_bit
            colour_flag = 0
        #print()        
    
    return 0

def remove_some_stuff(input_ext):
    scriptname = getframeinfo(currentframe()).filename
    cwd_path = os.path.dirname(os.path.abspath(scriptname))
    shutil.rmtree(os.fspath(PurePath(cwd_path,'frames_folder3')), ignore_errors=True)


def main(params_path):
    if not os.path.exists(params_path):
        print('Could not get parameters: no such file')
        sys.exit(1)
    with open(params_path) as f:
        lines = f.readlines()
        parsed_params_count = 0
        for line in lines:
            input_fname_match = re.search('(?<=INPUT_VIDEO_FILENAME=)\S*',line)
            if input_fname_match:
                input_video_fname = input_fname_match.group(0)
                print(f'Input video filename: {input_video_fname}')
                parsed_params_count+=1
            ratio_match = re.search('(?<=RATIO_COEF=)[0-9]*',line)
            if ratio_match:
                ratio = int(ratio_match.group(0))
                print(f'Ratio = {ratio}')
                parsed_params_count+=1
            mult_coef_match = re.search('(?<=MULTIPLY_COEF=)[0-9]*',line)
            if mult_coef_match:
                mult_coef = int(mult_coef_match.group(0))
                print(f'Message multiply coefficient = {mult_coef}')
                parsed_params_count+=1
        f.close()
    if parsed_params_count !=3:
        print('Could not parse all 3 parameters')
        sys.exit(2)
    if ratio<2:
        print('Ratio should have value equal to 2 or greater')
        sys.exit(3)
    if mult_coef<1:
        print('Message multiplication coefficient should have value equal to 1 or greater')
        sys.exit(4)
    allowed_input_extensions = ['.mkv']
    input_ext = os.path.splitext(input_video_fname)[1]
    if not(input_ext  in allowed_input_extensions):
        print("Input filename has unsupported extension")
        sys.exit(5)
    
    remove_some_stuff(input_ext)
    scriptname = getframeinfo(currentframe()).filename
    cwd_path = os.path.dirname(os.path.abspath(scriptname))

    if not os.path.exists(os.fspath(PurePath(cwd_path,'uses_count.txt'))):
        print('uses_count.txt does not exist; creating uses_count.txt')
        count_f = open(os.fspath(PurePath(cwd_path,'uses_count.txt')),'w+')
    else:
        count_f = open(os.fspath(PurePath(cwd_path,'uses_count.txt')),'r+')
    count_read = count_f.read()
    if (len(count_read) == 0):
        count = 0
        count_f.write('0')
    else:
        count = int(count_read)
    print(f'uses count = {count}')
    count_f.seek(0)
    count_f.write('')      
    count_f.write(str(count+1))
        
    count_f.close()

    print('This is just a demonstration, in fact you will need to secretly(separately) calculate seed and evenness value')
    message_num = int(input('Enter number of message you want to get (1 or 2)'))
    if message_num not in [1,2]:
        print('Incorrect message number, enter it again')
        message_num = int(input('Enter number of message you want to get (1 or 2)'))
        if message_num not in [1,2]:
            print('Incorrect message number again, exiting')
            sys.exit(6)
    evenness_seed = 3652
    seed(evenness_seed + count)
    evenness = randint(0,1)
    if message_num == 1:
        first_init_seed = 5764
        seed(first_init_seed+count)
        seed_val = randint(0,10000)     
    else:
        second_init_seed = 7453
        seed(second_init_seed + count)
        seed_val = randint(0,10000)
        evenness = abs(evenness - 1)
    print(f'seed = {seed_val}')
    print(f'evenness = {evenness}')
    clip = VideoFileClip(input_video_fname, fps_source="fps")
    print(f'Videofile duration = {clip.duration}')

    input_seed = int(input("Enter seed: "))
    input_evenness = int(input("Enter evenness: "))
    get_msg_from_video(input_video_fname, input_seed,input_evenness,ratio,mult_coef)
    remove_some_stuff(input_ext)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('ParamsPath',
                    type=str,
                    help='Path to .txt file with parameters')
    args = parser.parse_args()
    params_path = args.ParamsPath
    main(params_path)

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


def put_msg_in_frames(msg_filename,seed_val,evenness,ratio,mult_coef):
    scriptname = getframeinfo(currentframe()).filename
    cwd_path = os.path.dirname(os.path.abspath(scriptname))
    directory=sorted(os.listdir(os.fspath(PurePath(cwd_path,'frames_folder'))))
    fnames = []
    for fname in directory:
        if int(ord(fname[-5]) - ord('0')) % 2 == evenness:
            fnames.append(fname)
    width, height = Image.open(os.fspath(PurePath(cwd_path,'frames_folder',fnames[0]))).convert('RGBA').size
    px_num = width*height
    maxlen = floor((len(fnames)*3*px_num/(ratio * mult_coef))/8)
    print(f'message should be {maxlen} bytes long')
    with open(msg_filename,'r') as f:
        first_msg_once = f.read()
        print(f'length of message from file is {len(first_msg_once)} bytes')
        if (len(first_msg_once) > maxlen):
            print('message is too long')
            return -1
        print(f'message : {first_msg_once}')
        if(len(first_msg_once) < maxlen):
            first_msg_once += (maxlen - len(first_msg_once))*' '
        first_msg = mult_coef*first_msg_once
        print(first_msg)
        f.close()
    print(f'seed = {seed_val}')
    bytes_one = bytearray()
    bytes_one.extend(map(ord, first_msg))
    print(f'message length = {len(bytes_one)}')
    offset = 0
    bits_per_frame = float(mult_coef*maxlen*8)/float(len(fnames))
    print(f'bits per frame = {bits_per_frame}, rounded to {ceil(bits_per_frame)}')
    bits_per_frame = ceil(bits_per_frame)
    seed(seed_val)
    ret = 0
    for fname in fnames:
        if ret == -1:
            frame = Image.open(os.fspath(PurePath(cwd_path,'frames_folder',fname))).convert('RGBA')
            frame.save(os.fspath(PurePath(cwd_path,'frames_folder2',fname)), "PNG")
        else:
            ret = put_msg_in_img(os.fspath(PurePath(cwd_path,'frames_folder',fname)), os.fspath(PurePath(cwd_path,'frames_folder2',fname)), bytes_one, bits_per_frame, offset)
            if ret == 0:
                offset+=bits_per_frame
    return 0

def put_msg_in_img(frame_path,save_path, msg_bytes, bits_number, offset):
    print(frame_path)
    frame = Image.open(frame_path).convert('RGBA')
    width, height = frame.size

    util_pxs  = []
    colour_flag = 0
    for bit_index_in_msg in range(bits_number):
        if (offset+bit_index_in_msg >= (len(msg_bytes)*8)):
            return -1
        index_in_byte = ((offset + bit_index_in_msg)%8)
        if(index_in_byte == 0):
            print('New byte:')
        byte_index = (offset + bit_index_in_msg)//8
        msg_bit = bool(msg_bytes[byte_index] % (2**((7-index_in_byte)+1)) - msg_bytes[byte_index] % (2**(7-index_in_byte)))
        
        if colour_flag == 0:
            flag = 1
            while flag:
                px_x = randint(0,width - 1)
                px_y = randint(0,height - 1)
                if len(util_pxs):
                    for util_px_index in range(len(util_pxs)):
                        if (util_pxs[util_px_index] == px_x and util_pxs[util_px_index] == px_y):
                            break
                        elif util_px_index == (len(util_pxs)-1):
                            flag = 0
                            break
                else:
                    break
            util_pxs.append([px_x,px_y])
            r, g, b, a = frame.getpixel((px_x, px_y))
           
            #print(f'         r = {bin(r)}')
            r>>=1
            #print(f'modified r = {bin(r)}')
            r<<=1
            #print(f'modified r = {bin(r)}')
            r += msg_bit
            print(f'{bit_index_in_msg})  embedding {int(msg_bit)} in ({px_x}, {px_y}) => R({r})')
            #print(f'modified r = {bin(r)}')
            frame.putpixel((px_x, px_y), (r, g, b, a))
            frame.save(save_path, "PNG")
            colour_flag = 1
        elif colour_flag == 1:
            #print(f'         b = {bin(b)}')
            b>>=1
            #print(f'modified b = {bin(b)}')
            b<<=1
            #print(f'modified b = {bin(b)}')
            b += msg_bit
            
            print(f'{bit_index_in_msg})  embedding {int(msg_bit)} in ({px_x}, {px_y}) => B({b})')
            #print(f'modified b = {bin(b)}')
            frame.putpixel((px_x, px_y), (r, g, b, a))
            frame.save(save_path, "PNG")
            colour_flag = 2
        elif colour_flag == 2:
            #print(f'         g = {bin(r)}')
            g>>=1
            #print(f'modified g = {bin(r)}')
            g<<=1
            #print(f'modified g = {bin(r)}')
            g += msg_bit
            print(f'{bit_index_in_msg})  embedding {int(msg_bit)} in ({px_x}, {px_y}) => G({g})')
            frame.putpixel((px_x, px_y), (r, g, b, a))
            frame.save(save_path, "PNG")
            colour_flag = 0
        #print()        
    return 0

def assemble_video(orig_fps,output_fname):
    print()
    print()
    print('Assembling modified video from frames:')
    scriptname = getframeinfo(currentframe()).filename
    cwd_path = os.path.dirname(os.path.abspath(scriptname))
    directory=sorted(os.listdir(os.fspath(PurePath(cwd_path,'frames_folder2'))))
    print(f'{len(directory)} frames')
    
    fnames_t = os.fspath(PurePath(cwd_path,'frames_folder2','frame%09d.png'))
    output_ext = os.path.splitext(output_fname)[1]
    assembled_no_sound_path = os.fspath(PurePath(cwd_path,'assembled_no_sound'+ output_ext))
    os.system(f'ffmpeg -framerate {orig_fps} -i {fnames_t} -codec copy {assembled_no_sound_path}')
    if os.path.exists(os.fspath(PurePath(cwd_path,"audio.wav"))):
        audio_path = os.fspath(PurePath(cwd_path,'audio.wav'))
        os.system(f'ffmpeg  -i {assembled_no_sound_path} -i {audio_path} -codec copy {output_fname}')
    else:
        shutil.move(assembled_no_sound_path,output_fname)

def remove_some_stuff(input_ext,output_ext):
    scriptname = getframeinfo(currentframe()).filename
    cwd_path = os.path.dirname(os.path.abspath(scriptname))
    shutil.rmtree(os.fspath(PurePath(cwd_path,'frames_folder')),  ignore_errors=True)
    shutil.rmtree(os.fspath(PurePath(cwd_path,'frames_folder2')), ignore_errors=True)
    if os.path.exists(os.fspath(PurePath(cwd_path,'audio.wav'))): os.remove(os.fspath(PurePath(cwd_path,'audio.wav')))
    if os.path.exists(os.fspath(PurePath(cwd_path,'cut' + input_ext))): os.remove(os.fspath(PurePath(cwd_path,'cut' + input_ext)))
    if os.path.exists(os.fspath(PurePath(cwd_path,'assembled_no_sound' + output_ext))): os.remove(os.fspath(PurePath(cwd_path,'assembled_no_sound' + output_ext)))


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
            output_fname_match =  re.search('(?<=OUTPUT_VIDEO_FILENAME=)\S*',line)
            if output_fname_match:
                output_video_fname = output_fname_match.group(0)
                print(f'Output video filename: {output_video_fname}')
                parsed_params_count+=1
            message1_fname_match = re.search('(?<=MESSAGE1_FILENAME=)\S*',line)
            if message1_fname_match:
                message1_fname = message1_fname_match.group(0)
                print(f'First message filename: {message1_fname}')
                parsed_params_count+=1
            message2_fname_match = re.search('(?<=MESSAGE2_FILENAME=)\S*',line)
            if message2_fname_match:
                message2_fname = message2_fname_match.group(0)
                print(f'Second message filename: {message2_fname}')
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
    if parsed_params_count !=6:
        print('Could not parse all 6 parameters')
        sys.exit(2)
    if ratio<2:
        print('Ratio should have value equal to 2 or greater')
        sys.exit(3)
    if mult_coef<1:
        print('Message multiplication coefficient should have value equal to 1 or greater')
        sys.exit(4)
    allowed_input_extensions = ['.avi','.mkv','.mp4']
    allowed_output_extensions = ['.mkv']
    input_ext = os.path.splitext(input_video_fname)[1]
    output_ext = os.path.splitext(output_video_fname)[1]
    if not(input_ext  in allowed_input_extensions):
        print("Input filename has unsupported extension")
        sys.exit(5)
    if not(output_ext  in allowed_output_extensions):
        print("Output filename has unsupported extension")
        sys.exit(6)
    
    remove_some_stuff(input_ext,output_ext)
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

    first_init_seed = 5764
    seed(first_init_seed+count)
    first_seed = randint(0,10000)                                         
    print(f'first seed = {first_seed}')
    second_init_seed = 7453
    seed(second_init_seed + count)
    second_seed = randint(0,10000)
    print(f'second seed = {second_seed}')
    evenness_seed = 3652
    seed(evenness_seed + count)
    evenness = randint(0,1)
    print(f'evenness = {evenness}')
    old_clip = VideoFileClip(input_video_fname, fps_source="fps")
    int_duration = int(old_clip.duration)
    if(int_duration == 0):
        print("Input container is too short")
        sys.exit(7)
    print(f'Input videofile duration = {old_clip.duration}')
    hours = int_duration//3600
    hours_str = str(hours)

    if(len(hours_str)>2):
        print("Input container is too long")
        sys.exit(8)
    if(len(hours_str) == 1):
        hours_str = '0' + hours_str

    mins = (int_duration - 3600*(int_duration//3600))//60
    mins_str = str(mins)
    if(len(mins_str) == 1):
        mins_str = '0' + mins_str

    secs = (int_duration - hours*3600 - mins*60) % 60
    secs_str = str(secs)
    if(len(secs_str) == 1):
        secs_str = '0' + secs_str
    input_ext = os.path.splitext(input_video_fname)[1]
    cut_path = os.fspath(PurePath(cwd_path,'cut' + input_ext))
    os.system(f'ffmpeg -i {input_video_fname} -ss 00:00:00 -t {hours_str}:{mins_str}:{secs_str} -async 1 {cut_path}')
    
    Path(os.fspath(PurePath(cwd_path,'frames_folder'))).mkdir()
    Path(os.fspath(PurePath(cwd_path,'frames_folder2'))).mkdir()
    
    clip = VideoFileClip(cut_path, fps_source="fps")
    if type(clip.audio)!=NoneType:
        clip.audio.write_audiofile(filename = os.fspath(PurePath(cwd_path,"audio.wav")))
    print(f'duration = {clip.duration}')
        
    print(f'fps = {clip.fps}')
    
    print('Embedding messages bytes into videofile frames:')
    clip.write_images_sequence(os.fspath(PurePath(cwd_path,'frames_folder','frame%09d.png')), logger='bar')
    ret = put_msg_in_frames(message1_fname,first_seed,evenness,ratio,mult_coef)
    if ret == -1:
        remove_some_stuff(input_ext,output_ext)
        sys.exit(9)
    ret = put_msg_in_frames(message2_fname,second_seed,abs(evenness - 1),ratio,mult_coef)
    if ret == -1:
        remove_some_stuff(input_ext,output_ext)
        sys.exit(10)
    assemble_video(clip.fps,output_video_fname)
    print(f'first seed = {first_seed}')
    
    print(f'second seed = {second_seed}')
    
    print(f'evenness = {evenness}')
    remove_some_stuff(input_ext,output_ext)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('params_path',
                    type=str,
                    help='Path to .txt file with parameters')
    args = parser.parse_args()
    params_path = args.params_path
    main(params_path)

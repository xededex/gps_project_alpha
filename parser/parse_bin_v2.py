import struct
from sys import argv
from datetime import datetime, timedelta
import os

def nmea_convert(lat_, type):
    
    intg_count = lat_.find('.') - 2
    if intg_count < 0:
        intg_count = 0
    min = lat_[intg_count : ]
    degress = 0 if lat_[: intg_count] == '' else lat_[: intg_count]

    new_lng = float(degress) + float(min) / 60

    if type == "W" or type == "S":
        new_lng *= -1

    print(new_lng)
    return new_lng



class ParseBinaryFile:

    cache_gpgga = []
    
    
    prefix_type_cmd = {
        "$" : "asc",
    }

    GPS_QUAL_CODE = {
        "0" : "fix not available or invalid",
        "1" : "GPS fix",
        "2" : "C/A differential GPS; OmniSTAR HP; OmniSTAR XP; OmniSTAR VBS; or CDGPS",
        "4" : "RTK fixed ambiguity solution (RT2)",
        "5" : "K floating ambiguity solution (RT20); OmniSTAR HP or OmniSTAR XP",
        "6" : "Dead reckoning mode",
        "7" : "Manual input mode (fixed position)",
        "8" : "Super wide-lane mode",
        "9" : "SBAS",
    }
    bytes_read = 0
    id_to_offset = {
        'header' : 28,
        '140' : 'RANGECMP',
        '181' : 'MARKPOS',
        '231' : 'MARKTIME',
        '42'  : 'BESTPOS',
    }


    pos_type_map = {
        '0'   : "No solution",
        '1'   : "Position has been fixed by the FIX POSITION command",
        '8'   : "Velocity computed using instantaneous Doppler",
        '16'  : "Single point position",
        '17'  : "Pseudorange differential solution",
        '18'  : "Solution calculated using corrections from an SBAS",
        '34'  : "floating narrow-lane ambiguity solution",
        '35'  : "Derivation solution",
        '49'  : "Integer wide-lane ambiguity solution",
        '51'  : "Super wide-lane solution",
        '64'  : "OMNISTAR_HP", 
        '65'  : "OMNISTAR_XP", 
        '68'  : "Converging TerraStar-C, TerraStar-C PRO or TerraStar-X solution",
        '69'  : "Converged PPP solution",
        '70'  : "Solution accuracy is within UA Loperational limit",
        '71'  : "Solution accuracy is outside UAL operational limit but within warning limit",
        "72"  : "Solution accuracy is outside UAL limits",
        
    }

    close_file   = False


    need_log_command = [181, 231]
    def __init__(self, path_to_file, path_to_log) -> None:
        self.pref_bin_command   = b'\xaaD\x12\x1c'
        self.pref_ascii_command = b'$GPGGA'
        self.ind_ascii = 0
        self.ind = 0      
        self.map_command = {"GPGGA" : 0}
        # self.count_command = 0
        self.iter = 1
        self.iter_ascii = 1
        
        self.name_parsing_file = path_to_file.split('.')[0]
        os.mkdir(self.name_parsing_file)
        self.curr_gps_qual        = '0'
        current_datetime          = datetime.now()
        self.f_output_gpga        = open(self.name_parsing_file + "/" + f"{self.name_parsing_file}_GPGGA"   + ".csv", "w")
        self.f_output_markpos     = open(self.name_parsing_file + "/" + f"{self.name_parsing_file}_MARKPOS" + ".csv", "w")
        # self.f_output_marktime    = open("MAKRTIME" + f"_{current_datetime}.csv", "w")
        self.f_                    = open(path_to_file, 'rb')
        self.f                     = self.f_.read()

        self.f_output_gpga.writelines('num, lat_, lon_, GPS_qual, sats' + "\n")
        self.f_output_markpos.writelines('num, lat, lon, hgt, utc, GPS_qual' + "\n")
        # self.f_output_marktime.writelines(f'week, seconds, offset, offset_std, utc_offset, utc' + "\n")
        print(current_datetime)
        
    def search_near_gps_qual(self, lat, lon):
        transorm_to_distance = [[(i["lat"] - lat) ** 2 + (i["lon"] - lon) ** 2, i["GPS qual"]] for i in self.cache_gpgga] 
        min_distance = min(transorm_to_distance, key = lambda x : x[0]) 
        return min_distance[1] 

    def __del__(self):
        self.f_output_gpga.close()
        self.f_output_markpos.close()
        self.f_.close()


    def log_command_to_file(self, cmd):
        
        if (cmd["type"] == "bin" and cmd["name"] == "MARKPOS"):
            self.f_output_markpos.writelines(f"{int(self.iter / 2)}, {cmd['lat']}, {cmd['lon']}, {cmd['hgt']}")
            self.cached_lat = cmd['lat']
            self.cached_lon = cmd['lon']
        
        elif (cmd["type"] == "bin" and cmd["name"] == "MARKTIME"):
            near_gps_qual = self.search_near_gps_qual(self.cached_lat, self.cached_lon)
            self.f_output_markpos.writelines(f", {cmd['utc_time']}, {self.GPS_QUAL_CODE[near_gps_qual]}" + '\n' )

            # self.f_output_markpos.writelines(f", {cmd['utc_time']}, {self.GPS_QUAL_CODE[self.curr_gps_qual]}" + '\n' )
        elif (cmd["type"] == 'ascii' and cmd['name'] == '$GPGGA'):
            lat = nmea_convert(cmd["lat"], cmd["latdir"])
            lon = nmea_convert(cmd["lon"], cmd["londir"])
            self.curr_gps_qual = cmd['GPS qual']
            self.f_output_gpga.writelines(f"{self.iter_ascii}, {lat}, {lon}, {self.GPS_QUAL_CODE[cmd['GPS qual']]}, {cmd['sats']}" + "\n")
            # lng = nmea_convert('-7.66548', 'S')
            # lat = nmea_convert('5130.44106', 'W')
            print(lat, lon)



            # intg_count = lat_.find('.') - 2
            # if intg_count < 0:
            #     intg_count = 0
            # min = lat_[intg_count : ]
            # degress = lat_[: intg_count]

            # new_lng = float(degress) + float(min) / 60
            # print(new_lng)
            # lat_ = cmd["lat"]
            


            # lat  = float(lat_[ : 2]) + (float(lat_[2 : ]) / 60 )
            # print(lat)
           
            # lon_ = '-7.66548'
            # lon  = float(lon_[ : 3]) + (float(lon_[3 : ]) / 60 )
            # print(lon)
        
                # lon = intg / 100 + (dbl / (100 * 60 * (len(str(dbl)) + 1))) * -1 

            
            
            # self.f_output_markpos.writelines(f", {cmd['utc_time']}" + '\n' )



    def init_log(self, path):
        pass

    def cached_gpgga_command(self, cmd):
        lat_ = nmea_convert(cmd['lat'], cmd['latdir'])
        lon_ = nmea_convert(cmd['lon'], cmd['londir'])
        self.cache_gpgga.append({"lat": lat_, "lon" : lon_, "GPS qual" : cmd["GPS qual"]})
        
        
    def is_asc_command(self):
        return ord(self.f.peek(1)[:1]) == ord("$") 


    def parse_asci_command(self, cmd):
        
        
        cmd = cmd.split(',')
        obj_command = {}
        if (cmd[0] == "$GPGGA"):
            obj_command = {
                "type"       : "ascii",
                "name"       : "$GPGGA",
                "utc"        : cmd[1],
                "lat"        : cmd[2],
                "latdir"     : cmd[3],
                "lon"        : cmd[4],
                "londir"     : cmd[5],
                "GPS qual"   : cmd[6],
                "sats"       : cmd[7],
                "hdop"       : cmd[8],
                "alt"        : cmd[9],
                "a-units"    : cmd[10],
                "undulation" : cmd[11],
                "u-units"    : cmd[12],
                "age"        : cmd[13],
                "stn ID"     : cmd[14],
            }
            if self.iter_ascii % 10 == 0:
                self.cached_gpgga_command(obj_command)
            
            print(obj_command)
            return obj_command

        print(cmd)

    def parse_bin_command(self, id, len):
        if (self.id_to_offset[str(id)] == 'MARKPOS'):
            print("MARKPOS_____MARKPOS_____MARKPOS___MARKPOS_____MARKPOS_____MARKPOS___")
            body = self.f[self.ind + 36 : self.ind + 36 + 24]
            dc   = struct.unpack('<3d', body)
            
            
            # sol_stat, pos_type = struct.unpack('<2I', self.f.read(8))
            # word = self.f.read(24)
            # dc   = struct.unpack('<3d', word)
            # self.f.read(24)
            # diff_age, sol_age = struct.unpack('<2f', self.f.read(8))
            obj_command = {
                "type" : "bin",
                "name" : "MARKPOS",
                "lat"  : dc[0],
                "lon"  : dc[1],
                "hgt"  : dc[2],

            }
            # self.f_output_markpos.writelines(f"{dc[0]}, {dc[1]}, {dc[2]}, {diff_age}, {sol_age}, {self.pos_type_map[str(pos_type)]}")
            
            # print(diff_age, sol_age)
            # print(dc)
            # magic_const = 8 + 24 + 32               # Считали даннное кол-во байт для того, что бы получить необходимые значения
            # self.f.read(len - magic_const + 4)      # Перемещаемся к следующей команде
            return obj_command
            
            
            # return (8 + 24 + 32)
        
        elif (self.id_to_offset[str(id)] == 'MARKTIME'):
            print("MARKTIME_____MARKTIME_____MARKTIME___MARKTIME_____MARKTIME_____MARKTIME___")
            body = self.f[self.ind + 28 : self.ind + 28 + 36]
            word   = struct.unpack('<l4d', body)
            print(word)

            
            # word = self.f.read(4 + 8 * 4)
            # word = struct.unpack('<l4d', word)
            # print(word)
            
            sec_from_week   = float(word[0]) * 604800
            sec_from_week  +=  float(word[1])
            utc_time        = datetime(1980, 1, 6) + timedelta(seconds=sec_from_week - (35 - 19))
            
            # self.f_output_markpos.writelines(f", {utc_time}" + '\n' )
            obj_command = {
                "type"       : "bin",
                "name"       : "MARKTIME",
                "week"       : word[0],
                "seconds"    : word[1],
                "offset"     : word[2],
                "offset_std" : word[3],
                "utc offset" : word[4],
                "utc_time"   : utc_time,
            }
            # self.f_output_marktime.writelines(f"{word[0]}, {word[1]}, {word[2]}, {word[3]}, {word[4]}, {utc_time}" + '\n')
            # magic_const = 4 + 8 * 4                 # Считали даннное кол-во байт для того, что бы получить необходимые значения
            # self.f.read(len - magic_const + 4)      #Перемещаемся на n байт вперед к следующей команде
            return obj_command

        elif (self.id_to_offset[str(id)] == 'BESTPOS'):

            pass
        

        # else:
        #     self.f.read(len + 4)

        #     return {
        #         "type" : "bin", 
        #         "id"   : id,
        #         "len"  : len,
        #     }
        #     # return (4 + 8 * 4)

    def next_ascii_command(self):
        self.ind_ascii = self.f.find(b"$GPGGA", self.ind_ascii)
        if (self.ind_ascii == -1):
            return False
        ind_end = self.f.find(b"\n", self.ind_ascii)
        cmd = self.f[self.ind_ascii : ind_end].decode('ascii')
        self.map_command["GPGGA"] += 1
        obj_command = self.parse_asci_command(cmd)
        self.log_command_to_file(obj_command)
        print(obj_command)
        self.ind_ascii = ind_end
        return True



    def next_bin_command(self):
        self.ind = self.f.find(self.pref_bin_command, self.ind)
        if (self.ind == -1):
            return False
        
        word = self.f[self.ind + 3: self.ind + 10]
        unpack_ = struct.unpack('<BH2cH', word)
        id_command = unpack_[1]
        self.map_command[id_command] = 1 if id_command not in self.map_command else self.map_command[id_command] + 1
        id = unpack_[1]
        # if(self.is_asc_command()):
        #     s = self.f.readline().decode('ascii')
        #     obj_command = self.parse_asci_command(s)
        #     self.log_command_to_file(obj_command)
        #     print(obj_command)

        
        # id, len = self.get_header()
        if (id in self.need_log_command):
            self.iter += 1
            cmd = self.parse_bin_command(id, 12)
            self.log_command_to_file(cmd)
            print(cmd)
            
        self.ind += 24
        # self.count_command += 1
        return True
            
            # else:
            #     self.f.read(len + 4)
                                                                   #(GPS qual)
            # l = self.f.read(len + 4)
            # if (len > 0):
            #     l = self.f.read(len + 4)
            # return id, len



    def get_header(self):

        # ch = self.f.peek(1)[:1]
        # if ord(ch) == ord('$'):
        #     print("test")
        #     s = self.f.readline().decode('ascii')
        #     r = s.split(',')[0] 
        #     print(r)
        #     print(s)
        #     return 0, -4
        
        
        word = self.f.read(6)
        id   = int(struct.unpack('<3cBH', word)[4])
        self.f.read(2)
        word = self.f.read(2)
        len  = int(struct.unpack('<H', word)[0])
        self.f.read(18)
        
        print('id',  id)
        print('len', len)
        return id, len


    def test(self):
        # while (not self.next_command()[0] == 181):
        while(self.next_ascii_command()):
            print(self.ind_ascii)
            self.iter_ascii += 1
        while(self.next_bin_command()):
            print(self.ind)
       
            
        print(self.map_command)
            
        # self.f_output_gpga.close()
        # self.f_output_markpos.close()
        # self.f.close()
            # self.next_command()
            # self.next_command()

        # self.next_command()


# offset_to_mark = 9 * 28



if __name__ == "__main__":
    absFilePath = os.path.abspath(__file__)
    path, filename = os.path.split(absFilePath)
    # print(abspath(__file__))
    # curr_dir = os.path.abspath(__file__)
    # curr_dir = '/'.join(curr_dir.split('/')[: -1])

    files = os.listdir(path)
    print(files)
    cnb_files = list(filter(lambda x: os.path.isfile(x) and x.split('.')[1] == "CNB", files))
    print(cnb_files)

        

    parse = [ParseBinaryFile(i, 'test').test() for i in cnb_files]
    # parse.test()



# with open('markpos_marktime.CNB', 'rb') as f:
#     for _ in range(8):
#         word = f.read(6)
#         dc   = struct.unpack('<3cBH', word)
#         print('command', dc)

#         f.read(22)

#         word = f.read(8)
#         dc   = struct.unpack('<L4s', word)
#         offset = int(dc[0])
#         print(offset)
#         f.read(0 + offset * 24)

    

#     word = f.read(6)
#     dc   = struct.unpack('<3cBH', word)
#     print('command', dc)
#     f.read(22)

#     f.read(8)
    
#     word = f.read(24)
#     dc   = struct.unpack('<3d', word)
#     print(dc)


    

    # f.read(86)
    # word = f.read(6)
    # dc   = struct.unpack('<3cBH', word)    
    # print('command', dc)

    # f.read(8)
    # word = f.read(24)
    # dc   = struct.unpack('<3d', word)
    # print(dc)
    
    
    # f.read(44)
    # f.read(70)

    # word = f.read(6)
    # dc   = struct.unpack('<3cBH', word)
    # f.read(22)
    # print('command', dc)















# f    = open('markpos_marktime.CNB', 'rb')
# f.read(28)







# word = f.read(8)
# dc   = struct.unpack('<L4s', word)
# offset = int(dc[0])
# print(offset)
# print(dc)






# word = f.read(6)
# dc   = struct.unpack('<3cBH', word)
# print("next_comand", dc)




# f.read(22)



# word = f.read(8)
# dc   = struct.unpack('<L4s', word)
# offset = int(dc[0])
# print(offset)
# print(dc)


# f.read(0 + offset * 24)



# word = f.read(6)
# dc   = struct.unpack('<3cBH', word)
# print("next_comand", dc)

# f.read(22)



# word = f.read(8)
# dc   = struct.unpack('<L4s', word)
# offset = int(dc[0])
# print(offset)
# print(dc)


# f.read(0 + offset * 24)
# word = f.read(6)
# print("need: ", word)









# w = f.read(12)
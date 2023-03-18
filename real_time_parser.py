from datetime import datetime, timedelta
import struct


def convert_date_to_utc(week, seconds):
    sec_from_week   = float(week) * 604800
    sec_from_week  +=  float(seconds)
    utc_time        = datetime(1980, 1, 6) + timedelta(seconds=sec_from_week - (35 - 19))
    return utc_time




    




class Bin_Parser:
    
    iter_pos = 0
    iter_time = 0
    test_log_markpos = open("test_output_markpos.log", "w")
    test_log_marktime = open("test_output_marktime.log", "w")

    map_command = {"GPGGA" : 0}
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
    
    id_to_offset = {
        'header' : 28,
        '140' : 'RANGECMP',
        '181' : 'MARKPOS',
        '231' : 'MARKTIME',
        '42'  : 'BESTPOS',
    }
   
   
    def __init__(self, *args, **kwargs):
        self.history_command = []
        self.pref_bin_command   = b'\xaaD\x12\x1c'
        self.pref_ascii_command = [b'$GPGGA', b'#MARKPOSA', b'#MARKTIMEA']
        self.end_ascii_command = b'\n'
        self.buff = b""
        self.iter = 0
   
    def nmea_convert(self, lat_, type):
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
    
    
    def parse_header(self, cmd):
        word = cmd[3 : 10]
        unpack_ = struct.unpack('<BH2cH', word)
        print(unpack_)
        id_command = unpack_[1]
        id = unpack_[1]
        return id, unpack_
    



    def parse_bin_cmd(self, cmd):
        id, header = self.parse_header(cmd)
        
        if (self.id_to_offset[str(id)] == 'RANGECMP'):
            
            return {
                "type"  : "bin",
                "name"  : "RANGECMP",
                "text"  :   str(header),
            }
            
        elif (self.id_to_offset[str(id)] == 'MARKPOS'):
            
            self.iter_pos += 1
            print("MARKPOS_____MARKPOS_____MARKPOS___MARKPOS_____MARKPOS_____MARKPOS___")
            body = cmd[36 : 36 + 24]
            dc   = struct.unpack('<3d', body)
            self.test_log_markpos.writelines(f"{self.iter_pos}, {dc}")
            
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
            self.history_command = obj_command
            return obj_command
            
            
            # return (8 + 24 + 32)
        
        elif (self.id_to_offset[str(id)] == 'MARKTIME'):
            self.iter_time += 1

            print("MARKTIME_____MARKTIME_____MARKTIME___MARKTIME_____MARKTIME_____MARKTIME___")
            body = cmd[28 : 28 + 36]
            word   = struct.unpack('<l4d', body)
            self.test_log_markpos.writelines(f"{self.iter_time}, {word}")

            print(word)


            
           
            
            # self.f_output_markpos.writelines(f", {utc_time}" + '\n' )
            obj_command = {
                "type"        : "bin",
                "name"        : "full_cmd",
                "week"        : word[0],
                "seconds"     : word[1],
                "offset"      : word[2],
                "offset_std"  : word[3],
                "utc offset"  : word[4],
                # "utc_time"    : utc_time,
            }
            
            merged_cmd = obj_command | self.history_command
            merged_cmd["name"] = "FULL_CMD"
            self.history_command = ''
            return merged_cmd
    
    
    def search_bin_command(self):
        pos_pref = self.buff.find(self.pref_bin_command)
        if pos_pref == -1:
            return False, -1, -1
        pos_end_bin = self.buff.find(self.pref_bin_command, pos_pref + 28)
        pos_end_ascii = self.buff.find(self.pref_ascii_command, pos_pref + 28)

        if pos_end_bin == -1 and pos_end_ascii == -1:
            return False, -1, -1
        
        pos_end = pos_end_bin if pos_end_bin > 0 else pos_end_ascii 
        return True, pos_pref, pos_end
            
    def search_ascii_command(self):
        
        searched_pos = []
        
        for pref in self.pref_ascii_command:
            pos_pref = self.buff.find(pref)
            if pos_pref != -1:
                searched_pos.append(pos_pref)
        
        
        
        if len(searched_pos) != 0:
            min_seached = min(searched_pos)
            pos_end  = self.buff.find(self.end_ascii_command, min_seached)
            if pos_end != -1:
                return min_seached, pos_end    
        
        return None, None

        
            
        # if pos_pref != -1 and pos_end != -1:
        #     return True, pos_pref, pos_end
        # else:
        #     return False, -1, -1
    
    
    cache_mark = []
    def logg(self, cmd):
        
        if cmd["name"] == "MARKPOSA":
            self.cache_mark.append(cmd)

        elif cmd["name"] == "MARKTIMEA":
            if len(self.cache_mark) != 0:
                mark_pos = self.cache_mark.pop()
                joined = cmd | mark_pos 
                joined["name"] = "FULL_CMD"
                return joined
            else:
                return cmd
        else:
            return cmd
             
        
        
            
    
    
    def try_get_command(self, data):
        
        self.buff += data
              
        # cond_bin, pos_start_bin, pos_end_bin = self.search_bin_command()
        pos_start_ascii, pos_end_ascii = self.search_ascii_command()
        
        if pos_start_ascii != None and pos_end_ascii != None:
            cmd = self.buff[pos_start_ascii : pos_end_ascii]
            getting_cmd = self.parse_ascii_cmd(cmd)
            self.buff = self.buff[pos_end_ascii + 1 : ]

            
            
            return self.logg(getting_cmd)
        return None
                
        # if cond_bin and cond_ascii:
        #     pos_start_min = min(pos_start_bin, pos_start_ascii)
        #     pos_end_min   = min((pos_end_bin, pos_end_ascii))
        #     if pos_start_min == pos_start_bin and pos_end_min == pos_end_bin:
        #         cmd = self.parse_bin_cmd(self.buff[pos_start_min : pos_end_min])
        #     else:
        #         cmd = self.parse_ascii_cmd(self.buff[pos_start_min : pos_end_min])
            
        #     self.buff = self.buff[pos_end_min :]

        #     return cmd


        # elif cond_bin:
        #     cmd = self.parse_bin_cmd(self.buff[pos_start_bin : pos_end_bin])
        #     self.buff = self.buff[pos_end_bin :]
        #     print(cmd)
        #     return cmd

        # elif cond_ascii:
        #     cmd = self.parse_ascii_cmd(self.buff[pos_start_ascii : pos_end_ascii])
        #     self.buff = self.buff[pos_end_ascii :]
        #     print(cmd)

        #     return cmd


        return None
    
    
    def parse_ascii_cmd(self, cmd):
        print("cmd", cmd)
        cmd_cache = cmd
        cmd_cache = cmd_cache.decode('ascii')
        cmd = cmd.decode('ascii')    
        cmd = cmd.split(',')
        obj_command = {}
        if (cmd[0] == "$GPGGA"):
            self.map_command["GPGGA"] += 1
            obj_command = {
                "type"       : "ascii",
                "name"       : "$GPGGA",
                "utc"        : cmd[1],
                "lat"        : cmd[2],
                "latdir"     : cmd[3],
                "lon"        : cmd[4],
                "londir"     : cmd[5],
                "GPS qual"   : self.GPS_QUAL_CODE[cmd[6]],
                "sats"       : cmd[7],
                "hdop"       : cmd[8],
                "alt"        : cmd[9],
                "a-units"    : cmd[10],
                "undulation" : cmd[11],
                "u-units"    : cmd[12],
                "age"        : cmd[13],
                "stn ID"     : cmd[14],
            }
            
            obj_command["lat"] = self.nmea_convert(obj_command["lat"], obj_command["latdir"])
            obj_command["lon"] = self.nmea_convert(obj_command["lon"], obj_command["londir"])
            # if self.iter_ascii % 10 == 0:
            #     self.cached_gpgga_command(obj_command)
            
            print(obj_command)
            return obj_command
        else:
            header, body = cmd_cache.split(";")
            body_el = body.split(",")
            if cmd[0] == "#MARKPOSA":
                return {
                    "type" : "ascii",
                    "name" : "MARKPOSA",
                    "lat"  : body_el[2],
                    "lon"  : body_el[3],
                    "hgt"  : body_el[4],
                }
                
                
            
            elif cmd[0] == "#MARKTIMEA":
                return {
                    "type" : "ascii",
                    "name" : "MARKTIMEA",
                    "week" : body_el[0],
                    "sec"  : body_el[1],
                    "utc"  : str(convert_date_to_utc(body_el[0], body_el[1])),
                }
            
            
      
            
            
            
            

"""
contains string-encoded images for use in various places in APItest's web
serving.
"""
#############################################################################
#
#     This Cplant(TM) source code is the property of Sandia National
#     Laboratories.
#
#     This Cplant(TM) source code is copyrighted by Sandia National
#     Laboratories.
#
#     The redistribution of this Cplant(TM) source code is subject to the
#     terms of the GNU Lesser General Public License
#     (see cit/LGPL or http://www.gnu.org/licenses/lgpl.html)
#
#     Cplant(TM) Copyright 1998, 1999, 2000, 2001, 2002 Sandia Corporation.
#     Under the terms of Contract DE-AC04-94AL85000, there is a non-exclusive
#     license for use of this work by or on behalf of the US Government.
#     Export of this program may require a license from the United States
#     Government.
#
#############################################################################


from twisted.web import resource

class img(resource.Resource):
    isLeaf = False
    def render(self,request):
        return ''


class img_tee25_png(resource.Resource):
    isLeaf = True

    def render(self,request):
        return '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x19\x00\x00\x00\x19\x08\x02\x00\x00\x00K\x8b\x124\x00\x00\x00\x06bKGD\x00\xff\x00\xff\x00\xff\xa0\xbd\xa7\x93\x00\x00\x00\tpHYs\x00\x00\x0cL\x00\x00\x0cL\x01\x00\x89O\xaa\x00\x00\x00\x07tIME\x07\xd4\x03\t\x16\x16\x1b\xf1\x85b:\x00\x00\x00\xa0IDATx\x01c\xfc\xff\xff?\x03n\xf0\xe8\xc1\xf3\x03\xfb\xcfB\xe4]\xdc\xcc\xa5\xa4Eq\xabe`\xc1#\x07\x94\xfa\xf7\xff\xff\x9f\xdf\x7f j\xf0\xdb\nT\xc3\x84\xdf,\x92dG\xcd")\xb8FD\xd8\x13H\xab\xc8\x01\xf6\xfa\xd5\xbb\x7f\xff\xfe!\x8b \xb3\x19\x19\x19I0\xeb\xdc\x99\x1b\xc8\x9a\xd1\xd8,\xac,\x835\xad\x92\xe0G#\x13\ra\x11\x014\xaf\xc1\xb9\xa4\x85\x97\xa8\x98\x90\xb4\x8c\x18\\3&c\xb0\x86\xd7\xa8\xbb0\xe3\n\x9f\xc8`\r/\x16`\xd6gb\xc2\xe9:&`\xeeg\x85\xe6\r`\xca\xc6\xe7C\x06\x06\x00kB\x1e\xcc[\n\x91\x99\x00\x00\x00\x00IEND\xaeB`\x82'


class img_tpixel_gif(resource.Resource):
    isLeaf = True
    def render(self,request):
        return 'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\xff\xff\xff!\xf9\x04\x01\n\x00\x01\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02L\x01\x00;'


class img_hline25_png(resource.Resource):
    isLeaf=True
    def render(self,request):
        return '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x19\x00\x00\x00\x19\x08\x02\x00\x00\x00K\x8b\x124\x00\x00\x00\x06bKGD\x00\xff\x00\xff\x00\xff\xa0\xbd\xa7\x93\x00\x00\x00\tpHYs\x00\x00\x0cL\x00\x00\x0cL\x01\x00\x89O\xaa\x00\x00\x00\x07tIME\x07\xd4\x03\t\x16\x1b"\x1b.\x94\x7f\x00\x00\x00jIDATx\x01c\xfc\xff\xff?\x035\xc0\xbf\x7f\xff\x18\xa9e\x16\xd0=L\xd4p\x13\xd4\x8cQ\xb3H\x0b\xcc\x91\x10^,\xcf\x9e\xbe\xa6Jreddd\xd9\xb3\xeb\xe4\x9f\xdf\x7fH\x0bdl\xaaYXY\x06k\xd83>\xbc\xff\xec\x1f5\x8a\n&`\x80Q%\xe0!\x018X\xc3k\xd4]\xd8\x128n\xb1A\x1b^\xc0z\r\xb7\xabI\x93\x01\x00\x96\xbd\x1f\xb9\x8c\x87\xa3\xeb\x00\x00\x00\x00IEND\xaeB`\x82'


class img_angle25_png(resource.Resource):
    isLeaf=True
    def render(self,request):
        return '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x19\x00\x00\x00\x19\x08\x02\x00\x00\x00K\x8b\x124\x00\x00\x00\x06bKGD\x00\xff\x00\xff\x00\xff\xa0\xbd\xa7\x93\x00\x00\x00\tpHYs\x00\x00\x0cL\x00\x00\x0cL\x01\x00\x89O\xaa\x00\x00\x00\x07tIME\x07\xd4\x03\t\x16\x0e\x1bs\x9e\xfac\x00\x00\x00\x8fIDATx\x01c\xfc\xff\xff?\x03n\xf0\xe8\xc1\xf3\x03\xfb\xcfB\xe4]\xdc\xcc\xa5\xa4Eq\xabe`\xc1#\x07\x94\xfa\xf7\xff\xff\x9f\xdf\x7f j\xf0\xdb\nT\xc3\x84\xdf,\x92dG\xcd")\xb8FD\xd8\x13H\xab\xc8\x01\xf6\xe6\xf5\x07d.\x1a\x9b\x91\x91\x91\x04\xb3\xce\x9e\xbe\x86\xa6\x1f\x99\xcb\xc2\xca2X\xd3*#\xfe\x1c\xfb\xed\xeb\x8fW\xaf\xde!\xfb\x05\x17\x9b\t\x18`\xf8\xcd\xc2\xa5\x13\xab\xf8`\r\xafQwa\x8d.\x9c\x82\x836\xbc^\xbf~\x8d\xd3\xd1$J\x00\x00\xf7\xd9%\xc8\x95Q\xa5\xf4\x00\x00\x00\x00IEND\xaeB`\x82'        


class img_vline25_png(resource.Resource):
    isLeaf=True
    def render(self,request):
        return '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x19\x00\x00\x00\x19\x08\x02\x00\x00\x00K\x8b\x124\x00\x00\x00\x06bKGD\x00\xff\x00\xff\x00\xff\xa0\xbd\xa7\x93\x00\x00\x00\tpHYs\x00\x00\x0cL\x00\x00\x0cL\x01\x00\x89O\xaa\x00\x00\x00\x07tIME\x07\xd4\x03\t\x16\x1a:\x11Y=h\x00\x00\x00qIDATx\x01c\xfc\xff\xff?\x03n\xf0\xe8\xe1\xf3\x83\xfb\xce@\xe4\x9d\xdd,\xa4\xa4Eq\xabe`\xc1#\x07\x94\xfa\xff\xef\xff\xef\xdf\x7f!j\xfe\xff\xfb\x87_1\x13~i\x92dG\xcd")\xb8\x18F\xc3k4\xbc\xd0C`4M\xa0\x87\x08~\xfehx\xe1\x0f\x1ft\xd9\xc1\x1a^,\xff\xfe\xfdcb\xc2\xe9:F&FVVf\x88g\x18q+\x03*\x00\x9a\x03\x00\xd3\x88\x18-4d\xbd}\x00\x00\x00\x00IEND\xaeB`\x82'



class img_snlbird_50_gif(resource.Resource):
    isLeaf = True
    def render(self, request):
        return "GIF89a2\x002\x00\x80\x00\x00\x00\x99\xcc\xff\xff\xff!\xf9\x04\x01\n\x00\x01\x00,\x00\x00\x00\x002\x002\x00\x00\x02\xd6\x8c\x1f\xa0\xcb\xed\xff\x90D\xb0\xda\x0b\xe6\xc1\xbc\xb3\xe9\x85\x9d$\x96\x16Ui\xea\xba\xa5\x86\xc3\xc6\xf2\xdb\xd0\xdf\x9c\xc08\xac\xab\xdc^\xebi~3\xa2\x0f\x83\xcb\xb9V\n\x9b0vI.eQ`\xc4\n\x91f\xb1W\xa7iY\xf5~\xbba\xe5xk\xee\xa6\xcf5q\xdb\xcdn\xc2\x17\xa8x\xafl'\x9fZ\xf9\xdb\xfa\xfdW\xa7\xa675Xx\xb7\xe7&(D\x88\x16\xc8g\xf8\x86\xc7x(\x99\xf88\x97\x01I\x97\xa9\xe9ER\x96\xb6I\xc99\xfadY)g\n(\xda\xb9\x08z\xd9\xfa\xe7'\xdb\xe9\xf9\xe9\xba\t;%;Yj\xbb\xeb\x19J\x13\xac\x96\x03\x12\xcb4<\x94|\xd4\x8c\xfc\\\xfc\xe4\xccK\xedh\x9d1\xcd\x1c=*\x96\xf4\xbd(w\r\xaeL\xda\x17\x12~>\xac>\xb2\xcd>.\xcd\xae\xf5\xbeR\x00\x00;"



class img_tab_active_gif(resource.Resource):
    isLeaf = True
    def render(self, request):
        return 'GIF89a\xfb\x00H\x00\x80\x00\x00\xbb\xbb\xcc\xff\xff\xff!\xfe\x15Created with The GIMP\x00!\xf9\x04\x01\n\x00\x01\x00,\x00\x00\x00\x00\xfb\x00H\x00\x00\x02\xe1\x8c\x8f\xa9\n\xed\x0f\xa3\x9c\xb4\xda\x8b\xb3\xde\xbc\xfb\x9f-\xe2h\x80\xe6\x89\xa6\xea\xca\xb6\xe4\x8b\xb4\xf2L\xd7\xf6\xdd\xc00\xce\xf7\xfe\xcf\xd3\x91\x80\xc4\xa2\xf1\x88\x11\x8a\x90\xcc\xa6\xd3\xa7d<\xa7\xd4\xea)\x1a\xb3j\xb7\xdc\t\xb6\xd4\r\x8b\xad\xdf\xb1\xf9\xcc\xc4\xa2\xd7l\xa8\xb2\r\x8f\xcf\xde\xf2\xba\xdd$\xbc\xeb\xf7\x1a\x1d\xff\x0f(\xb1\x13H\x18\xf8R\x88\xf87\x94\xc8x7\xd2\x08Y\xb7\x14I\xd9\xb6P\x89\xb9&\x95\xc9)\x96\xd0\t\x1a\x96\x15JJ\x06V\x8a:u\x9a\xca\x9a\xd6\xfa\n\x1b+;K[k{\x8b\x9b\xab\xbb\xcb\xdb\xeb\xfb\x0b\x1c,<L\\l|\x8c\x9c\xac\xbc\xcc\xdc\xec\xfc\x0c\x1d-=M]m}\x8d\x9d\xad\xbd\xcd\xdd\xed\xfd\r\x1e.>N^n~\x8e\x9e\xae\xbe\xce\xde\xee\xfe\x0e\x1f/?O_o\x7f\x8f\x9f\xaf\xbf\xcf\xdf\xef_\\\x00\x00;'



class img_tab_gif(resource.Resource):
    isLeaf = True
    def render(self, request):
        return 'GIF89a\xfb\x00H\x00\x91\x00\x00\xdd\xdd\xdd\xff\xff\xff\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x02\x00,\x00\x00\x00\x00\xfb\x00H\x00\x00\x02\xff\x94\x8f\xa9\x1a\xe0\x0f\xa3\x9c\xb4\xda\x8b\xb3\xde\xbc\xfb\x0ff\xcbH\x1aM\x88\xa6\xea\xca\xb6n[\xc6\xc8\xf9\xd6\xf6\x8d\xe7\xb9,\xd3\xfa\x0f\x0c\n\x83\xbc\x92o\x88L*\x97\xa2\xe2\xe2\xc8\x8cJ\xa7@\'\x83\x8a\xcdja\xd6\x03t\x0b\x0e\x8b%]\xd3\xf8\x8c\x1e\x97\xbf\xe9\xb6;\xd9e\xbf\xe7t\x9cU^\xcf\xebUN\xfc\xfe\x0f\xb8Q\xe4\x17XhH\xd6s\xa8\xb8X\x91\xc8\xf8\x08\x19C\x08IYgT\x89yH2\x99\xd9\x896\xc2\xe9)\x1a\xf64jj\x99\x10z\xba:\x95\xca\xfa\x9a6\x03;\xabfF{\xbbe\x8b\xbbK%\xa0\xca\x0b|\xf3\x1bL\xec2\\\x8c\x9cr\x9c\xcc\xec\xb1\xdc\x0c\x9d\xf1\x1cMM1]\x8d\xfdp\x9d\x8d\xbd\xcdM\xed\xfd\r\x1d.\xceL^\x8e|\x8eN\xac\xbe\x0e\xdc\xee\xbe\x0b\x1f\x7f;O?k\x7f\xff\x9a\xaf\xbf\xca\xdfo\xea\x1f@Q\x02\x07v*h\x10\x13\xc2\x84\x94\x162|\xe4\xf0\xe1\xa2\x88\x12\x0fQ\xacX\xe8"F@;\x1a7\xee\xe9\xe81\x0f\xc8\x90tF\x92|c\xf2d\x9b\x94*\xd1\xb0l9\xe6%\xcc02gn\xa9i3\x0b\xce\x9cTv\xf2\x94\xe2\xf3\'\x93\xa0B\x95\x10-\x8a\xe4(R!J\x97\x02)\x00\x00;'


# EOF

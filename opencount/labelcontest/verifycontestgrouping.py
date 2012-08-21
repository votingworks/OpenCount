import wx
import sys
from PIL import Image
import os

sys.path.append("..")
from util import pil2wxb


class VerifyContestGrouping(wx.Panel):
    def __init__(self, parent, ocrdir, dirList, equivs, reorder, reorder_inverse, mapping, mapping_inverse, callback):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.frame = parent
        self.callback = callback

        self.ocrdir = ocrdir
        self.dirList = dirList
        self.equivs = equivs
        self.reorder = reorder
        self.reorder_inverse = reorder_inverse
        self.mapping = mapping
        self.mapping_inverse = mapping_inverse
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.imagearea = wx.Panel(self, size=(1000, 700))
        datasizer =  wx.BoxSizer(wx.HORIZONTAL)
        self.sofar = wx.StaticText(self, -1, label="")
        datasizer.Add(self.sofar)
        isokaysizer = wx.BoxSizer(wx.HORIZONTAL)
        back = wx.Button(self, -1, label="Back")
        allow = wx.Button(self, -1, label="Yes")
        deny = wx.Button(self, -1, label="No")
        denyall = wx.Button(self, -1, label="Deny All")
        allowall = wx.Button(self, -1, label="Accpet All (dangerous)")
        back.Bind(wx.EVT_BUTTON, self.back)
        allow.Bind(wx.EVT_BUTTON, self.allow)
        deny.Bind(wx.EVT_BUTTON, self.deny)
        denyall.Bind(wx.EVT_BUTTON, self.deny_all)
        allowall.Bind(wx.EVT_BUTTON, self.allow_all)
        isokaysizer.Add(back)
        isokaysizer.Add(allow)
        isokaysizer.Add(deny)
        isokaysizer.Add((100, 0))
        isokaysizer.Add(denyall)
        isokaysizer.Add(allowall)
        self.sizer.Add(isokaysizer)
        self.sizer.Add(datasizer)
        self.sizer.Add((0,20))
        self.sizer.Add(self.imagearea)

        self.SetSizer(self.sizer)
        self.Layout()
        self.Fit()

        self.group_index = 0
        self.is_valid = {}
        self.processgroups = [i for i,x in enumerate(self.equivs) if len(x) > 1]

        self.load_next_group(0)
        self.show()


    def load_next_group(self, inc=1):
        self.index = 0
        self.orderedpaths = []

        self.group_index += inc

        if self.group_index+inc < 0:
            return
        if self.group_index >= len(self.processgroups):
            print "DONE"
            self.group_index = 0
            self.callback([(self.processgroups[k],v) for k,v in self.is_valid.items()])
            self.frame.Close(True)

        for ballot,contest in self.equivs[self.processgroups[self.group_index]]:
            #print ballot, contest
            ballotname = os.path.split(self.dirList[ballot])[1].split('.')[0]
            boundingbox = self.mapping_inverse[ballot,contest][1]
            ballotdir = os.path.join(self.ocrdir,ballotname+"-dir")
            boundingboxdir = os.path.join(ballotdir, '-'.join(map(str,boundingbox)))
            order = self.reorder[self.reorder_inverse[ballot,contest]][ballot,contest]
            images = [img for img in os.listdir(boundingboxdir) if img[-3:] != 'txt']
            images = sorted(images, key=lambda x: int(x.split('.')[0]))
            paths = [os.path.join(boundingboxdir,img) for img in images]
            self.orderedpaths.append(paths)

        if self.group_index not in self.is_valid:
            self.is_valid[self.group_index] = [None]*len(self.orderedpaths)
        return

    def back(self, x=None):
        self.index -= 1
        if self.index < 0:
            self.load_next_group(-1)
            self.index = len(self.orderedpaths)-1
        self.show()
        
    def allow_all(self, x=None):
        self.is_valid[self.group_index] = [True]*len(self.orderedpaths)
        self.load_next_group()
        self.show()

    def deny_all(self, x=None):
        self.is_valid[self.group_index] = [False]*len(self.orderedpaths)
        self.load_next_group()
        self.show()

    def allow(self, x=None):
        self.is_valid[self.group_index][self.index] = True
        self.inc_and_show()

    def deny(self, x=None):
        self.is_valid[self.group_index][self.index] = False
        self.inc_and_show()
    
    def inc_and_show(self):
        self.index += 1
        if self.index >= len(self.orderedpaths):
            self.load_next_group()
        self.show()

    def show(self):
        print self.is_valid
        self.sofar.SetLabel("On item %d of %d in group %d of %d."%(self.index+1,len(self.orderedpaths),self.group_index+1,len(self.processgroups)))
        curpaths = self.orderedpaths[self.index]
        self.imagearea.DestroyChildren()
        pos = 0
        for path in curpaths:
            pilimg = Image.open(path)
            img = wx.StaticBitmap(self.imagearea, -1, pil2wxb(Image.open(path)),
                                  pos=(0, pos))
            pos += pilimg.size[1]



if __name__ == '__main__':
    mapping = {(11, (67, 1006, 632, 1105)): (11, 1), (13, (48, 1407, 633, 1600)): (13, 1), (3, (642, 804, 1233, 1825)): (3, 1), (10, (648, 774, 1233, 1071)): (10, 6), (1, (51, 1407, 639, 1640)): (1, 3), (17, (648, 1635, 1243, 1828)): (17, 2), (13, (48, 1632, 633, 1898)): (13, 2), (0, (54, 1416, 633, 1602)): (0, 0), (4, (51, 774, 648, 1152)): (4, 3), (6, (645, 804, 1233, 1826)): (6, 1), (15, (42, 735, 641, 1190)): (15, 0), (10, (51, 1185, 648, 1378)): (10, 1), (4, (51, 1407, 648, 1603)): (4, 2), (12, (46, 768, 633, 1150)): (12, 3), (0, (54, 771, 633, 1149)): (0, 3), (8, (48, 138, 645, 737)): (8, 3), (3, (39, 735, 638, 1077)): (3, 0), (2, (39, 735, 639, 967)): (2, 0), (21, (48, 1182, 633, 1376)): (21, 0), (14, (39, 735, 640, 965)): (14, 0), (12, (646, 399, 1243, 737)): (12, 6), (15, (646, 810, 1233, 1826)): (15, 1), (0, (654, 177, 1243, 405)): (0, 5), (4, (633, 165, 1233, 733)): (4, 5), (11, (67, 1115, 630, 1186)): (11, 0), (8, (648, 174, 1233, 401)): (8, 4), (5, (51, 132, 633, 739)): (5, 4), (12, (46, 132, 633, 737)): (12, 4), (9, (47, 138, 653, 740)): (9, 4), (8, (48, 1182, 645, 1376)): (8, 1), (22, (39, 735, 639, 1075)): (22, 0), (5, (51, 1668, 633, 1938)): (5, 2), (10, (639, 399, 1233, 734)): (10, 5), (1, (51, 1182, 639, 1377)): (1, 2), (5, (51, 1182, 633, 1372)): (5, 0), (21, (48, 771, 646, 1152)): (21, 2), (6, (39, 735, 640, 964)): (6, 0), (7, (670, 810, 1234, 1823)): (7, 1), (21, (48, 127, 646, 739)): (21, 3), (16, (847, 768, 1233, 1075)): (16, 4), (18, (70, 810, 640, 963)): (18, 0), (20, (645, 1218, 1241, 1597)): (20, 2), (5, (654, 1071, 1243, 1372)): (5, 7), (4, (42, 135, 648, 733)): (4, 0), (4, (51, 1182, 648, 1377)): (4, 1), (16, (857, 167, 1243, 393)): (16, 6), (7, (69, 774, 638, 964)): (7, 0), (12, (46, 1407, 633, 1634)): (12, 1), (21, (48, 1407, 633, 1639)): (21, 1), (1, (42, 774, 639, 1152)): (1, 0), (4, (633, 774, 1233, 1071)): (4, 4), (17, (637, 603, 1243, 1190)): (17, 1), (5, (654, 697, 1243, 1041)): (5, 8), (9, (47, 1671, 618, 1937)): (9, 2), (21, (651, 397, 1233, 739)): (21, 6), (16, (654, 768, 857, 1075)): (16, 3), (5, (51, 1413, 633, 1636)): (5, 1), (21, (651, 174, 1233, 403)): (21, 5), (22, (653, 804, 1233, 1824)): (22, 2), (0, (54, 132, 633, 740)): (0, 4), (18, (673, 810, 1233, 1824)): (18, 1), (10, (42, 138, 639, 744)): (10, 0), (2, (664, 807, 1233, 1829)): (2, 1), (8, (48, 768, 645, 1152)): (8, 2), (1, (642, 165, 1233, 734)): (1, 4), (9, (647, 400, 1243, 740)): (9, 6), (9, (647, 177, 1243, 406)): (9, 5), (10, (639, 165, 1233, 395)): (10, 4), (16, (639, 167, 851, 393)): (16, 1), (9, (47, 1185, 618, 1376)): (9, 0), (8, (648, 395, 1233, 737)): (8, 5), (22, (39, 1107, 623, 1599)): (22, 1), (16, (45, 141, 641, 327)): (16, 0), (17, (39, 846, 575, 1867)): (17, 0), (12, (46, 1674, 633, 1936)): (12, 2), (13, (48, 132, 654, 737)): (13, 4), (0, (654, 399, 1243, 740)): (0, 6), (16, (847, 394, 1233, 737)): (16, 5), (19, (42, 735, 639, 1077)): (19, 0), (5, (51, 771, 633, 1152)): (5, 3), (20, (39, 846, 603, 1861)): (20, 0), (0, (54, 1641, 633, 1904)): (0, 2), (13, (48, 1182, 633, 1375)): (13, 0), (9, (47, 1407, 618, 1639)): (9, 1), (5, (643, 132, 1243, 404)): (5, 5), (10, (51, 774, 648, 1153)): (10, 3), (21, (640, 771, 1233, 1038)): (21, 4), (13, (48, 774, 654, 1150)): (13, 3), (10, (51, 1410, 648, 1604)): (10, 2), (12, (646, 177, 1243, 405)): (12, 5), (13, (666, 399, 1243, 737)): (13, 6), (16, (645, 394, 857, 737)): (16, 2), (17, (648, 1221, 1243, 1603)): (17, 3), (5, (654, 474, 1243, 703)): (5, 6), (9, (47, 771, 633, 1151)): (9, 3), (1, (42, 138, 639, 734)): (1, 1), (19, (642, 813, 1233, 1824)): (19, 1), (0, (54, 1188, 633, 1375)): (0, 1), (20, (645, 1629, 1241, 1822)): (20, 1), (20, (645, 588, 1241, 1186)): (20, 3), (11, (67, 819, 623, 992)): (11, 2), (8, (48, 1407, 645, 1601)): (8, 0), (11, (657, 813, 1233, 1828)): (11, 3), (12, (46, 1182, 633, 1375)): (12, 0), (13, (666, 177, 1243, 405)): (13, 5), (14, (677, 810, 1233, 1825)): (14, 1)}
    mapping_inverse = {(16, 6): (16, (857, 167, 1243, 393)), (12, 1): (12, (46, 1407, 633, 1634)), (13, 4): (13, (48, 132, 654, 737)), (15, 1): (15, (646, 810, 1233, 1826)), (21, 6): (21, (651, 397, 1233, 739)), (8, 5): (8, (648, 395, 1233, 737)), (5, 8): (5, (654, 697, 1243, 1041)), (4, 0): (4, (42, 135, 648, 733)), (9, 0): (9, (47, 1185, 618, 1376)), (5, 5): (5, (643, 132, 1243, 404)), (16, 3): (16, (654, 768, 857, 1075)), (12, 6): (12, (646, 399, 1243, 737)), (17, 2): (17, (648, 1635, 1243, 1828)), (14, 1): (14, (677, 810, 1233, 1825)), (0, 4): (0, (54, 132, 633, 740)), (1, 1): (1, (42, 138, 639, 734)), (8, 2): (8, (48, 768, 645, 1152)), (4, 5): (4, (633, 165, 1233, 733)), (9, 3): (9, (47, 771, 633, 1151)), (6, 0): (6, (39, 735, 640, 964)), (11, 0): (11, (67, 1115, 630, 1186)), (16, 0): (16, (45, 141, 641, 327)), (16, 5): (16, (847, 394, 1233, 737)), (0, 1): (0, (54, 1188, 633, 1375)), (3, 1): (3, (642, 804, 1233, 1825)), (13, 0): (13, (48, 1182, 633, 1375)), (18, 0): (18, (70, 810, 640, 963)), (20, 3): (20, (645, 588, 1241, 1186)), (21, 2): (21, (48, 771, 646, 1152)), (2, 1): (2, (664, 807, 1233, 1829)), (9, 4): (9, (47, 138, 653, 740)), (5, 1): (5, (51, 1413, 633, 1636)), (10, 3): (10, (51, 774, 648, 1153)), (12, 2): (12, (46, 1674, 633, 1936)), (13, 3): (13, (48, 774, 654, 1150)), (7, 1): (7, (670, 810, 1234, 1823)), (15, 0): (15, (42, 735, 641, 1190)), (20, 0): (20, (39, 846, 603, 1861)), (21, 5): (21, (651, 174, 1233, 403)), (4, 1): (4, (51, 1182, 648, 1377)), (5, 4): (5, (51, 132, 633, 739)), (10, 4): (10, (639, 165, 1233, 395)), (16, 4): (16, (847, 768, 1233, 1075)), (17, 1): (17, (637, 603, 1243, 1190)), (13, 6): (13, (666, 399, 1243, 737)), (0, 5): (0, (654, 177, 1243, 405)), (1, 0): (1, (42, 774, 639, 1152)), (22, 0): (22, (39, 735, 639, 1075)), (8, 3): (8, (48, 138, 645, 737)), (9, 2): (9, (47, 1671, 618, 1937)), (6, 1): (6, (645, 804, 1233, 1826)), (5, 7): (5, (654, 1071, 1243, 1372)), (11, 3): (11, (657, 813, 1233, 1828)), (16, 1): (16, (639, 167, 851, 393)), (12, 4): (12, (46, 132, 633, 737)), (19, 1): (19, (642, 813, 1233, 1824)), (0, 2): (0, (54, 1641, 633, 1904)), (1, 3): (1, (51, 1407, 639, 1640)), (3, 0): (3, (39, 735, 638, 1077)), (8, 0): (8, (48, 1407, 645, 1601)), (18, 1): (18, (673, 810, 1233, 1824)), (21, 1): (21, (48, 1407, 633, 1639)), (5, 0): (5, (51, 1182, 633, 1372)), (10, 0): (10, (42, 138, 639, 744)), (12, 3): (12, (46, 768, 633, 1150)), (13, 2): (13, (48, 1632, 633, 1898)), (20, 1): (20, (645, 1629, 1241, 1822)), (1, 4): (1, (642, 165, 1233, 734)), (21, 4): (21, (640, 771, 1233, 1038)), (4, 2): (4, (51, 1407, 648, 1603)), (9, 6): (9, (647, 400, 1243, 740)), (5, 3): (5, (51, 771, 633, 1152)), (10, 5): (10, (639, 399, 1233, 734)), (7, 0): (7, (69, 774, 638, 964)), (12, 0): (12, (46, 1182, 633, 1375)), (17, 0): (17, (39, 846, 575, 1867)), (13, 5): (13, (666, 177, 1243, 405)), (0, 6): (0, (654, 399, 1243, 740)), (22, 1): (22, (39, 1107, 623, 1599)), (8, 4): (8, (648, 174, 1233, 401)), (9, 1): (9, (47, 1407, 618, 1639)), (5, 6): (5, (654, 474, 1243, 703)), (11, 2): (11, (67, 819, 623, 992)), (10, 6): (10, (648, 774, 1233, 1071)), (16, 2): (16, (645, 394, 857, 737)), (12, 5): (12, (646, 177, 1243, 405)), (17, 3): (17, (648, 1221, 1243, 1603)), (14, 0): (14, (39, 735, 640, 965)), (19, 0): (19, (42, 735, 639, 1077)), (0, 3): (0, (54, 771, 633, 1149)), (1, 2): (1, (51, 1182, 639, 1377)), (22, 2): (22, (653, 804, 1233, 1824)), (8, 1): (8, (48, 1182, 645, 1376)), (4, 4): (4, (633, 774, 1233, 1071)), (11, 1): (11, (67, 1006, 632, 1105)), (0, 0): (0, (54, 1416, 633, 1602)), (21, 0): (21, (48, 1182, 633, 1376)), (10, 1): (10, (51, 1185, 648, 1378)), (13, 1): (13, (48, 1407, 633, 1600)), (20, 2): (20, (645, 1218, 1241, 1597)), (21, 3): (21, (48, 127, 646, 739)), (2, 0): (2, (39, 735, 639, 967)), (4, 3): (4, (51, 774, 648, 1152)), (9, 5): (9, (647, 177, 1243, 406)), (5, 2): (5, (51, 1668, 633, 1938)), (10, 2): (10, (51, 1410, 648, 1604))}
    reorder = {(16, 6): {(16, 6): [(0, 0), (1, 1)]}, (13, 4): {(13, 4): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13)]}, (1, 3): {(5, 1): [(3, 3), (2, 2), (1, 1), (0, 0)], (1, 3): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)], (9, 1): [(3, 3), (0, 0), (1, 1), (2, 2)], (21, 1): [(3, 3), (2, 2), (0, 0), (1, 1)]}, (12, 1): {(12, 1): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]}, (20, 3): {(20, 3): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13)]}, (18, 0): {(18, 0): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]}, (3, 0): {(3, 0): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7)], (19, 0): [(6, 6), (2, 2), (4, 4), (5, 5), (3, 3), (1, 1), (0, 0)], (22, 0): [(0, 5), (6, 6), (3, 3), (2, 2), (4, 4), (1, 1), (5, 0)]}, (11, 2): {(11, 2): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]}, (16, 2): {(16, 2): [(0, 0), (1, 1)]}, (2, 1): {(2, 1): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25)]}, (15, 1): {(15, 1): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25)]}, (17, 3): {(17, 3): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8)]}, (14, 0): {(14, 0): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]}, (9, 4): {(9, 4): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13)]}, (0, 3): {(0, 3): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8)], (12, 3): [(7, 7), (0, 0), (4, 4), (1, 1), (5, 5), (3, 3), (6, 6), (2, 2)]}, (18, 1): {(18, 1): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25)]}, (3, 1): {(3, 1): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25)]}, (2, 0): {(2, 0): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]}, (16, 3): {(16, 3): [(0, 0), (1, 1)]}, (4, 4): {(4, 4): [(0, 0), (1, 1), (2, 2)], (10, 6): [(0, 0), (1, 1)]}, (15, 0): {(15, 0): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)]}, (17, 0): {(17, 0): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25)]}, (20, 0): {(20, 0): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25)]}, (14, 1): {(14, 1): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25)]}, (11, 1): {(11, 1): [(0, 0), (1, 1), (2, 2)]}, (0, 4): {(0, 4): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13)]}, (1, 1): {(10, 0): [(12, 12), (4, 4), (9, 9), (6, 6), (7, 7), (1, 1), (2, 2), (3, 3), (0, 0), (11, 11), (8, 8), (5, 5), (10, 10)], (1, 1): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13)], (4, 0): [(12, 12), (4, 4), (1, 1), (3, 3), (9, 9), (2, 2), (11, 11), (6, 6), (5, 5), (7, 7), (8, 8), (0, 0), (10, 10)]}, (5, 4): {(5, 4): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13)]}, (0, 0): {(13, 1): [(2, 2), (0, 0), (1, 1)], (0, 0): [(0, 0), (1, 1), (2, 2), (3, 3)], (8, 0): [(2, 2), (0, 0), (1, 1)], (16, 0): [(2, 2), (0, 0), (1, 1)], (4, 2): [(2, 2), (0, 0), (1, 1)], (10, 2): [(2, 2), (0, 0), (1, 1)]}, (8, 2): {(8, 2): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8)]}, (16, 4): {(16, 4): [(0, 0), (1, 1)]}, (9, 3): {(9, 3): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8)], (21, 2): [(7, 7), (4, 4), (5, 5), (6, 6), (1, 1), (0, 0), (3, 3), (2, 2)]}, (6, 0): {(6, 0): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]}, (1, 4): {(4, 5): [(0, 0), (2, 2), (3, 3), (1, 1)], (1, 4): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]}, (17, 1): {(17, 1): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13)]}, (11, 0): {(11, 0): [(0, 0), (1, 1)]}, (21, 4): {(21, 4): [(0, 0), (1, 1), (2, 2)]}, (7, 1): {(7, 1): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25)]}, (0, 5): {(10, 4): [(0, 0), (1, 1)], (5, 6): [(0, 0), (1, 1)], (13, 5): [(0, 0), (1, 1)], (12, 5): [(0, 0), (1, 1)], (0, 5): [(0, 0), (1, 1), (2, 2)], (21, 5): [(0, 0), (1, 1)], (9, 5): [(0, 0), (1, 1)], (8, 4): [(0, 0), (1, 1)]}, (16, 5): {(16, 5): [(0, 0), (1, 1)]}, (1, 0): {(1, 0): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8)], (10, 3): [(7, 7), (6, 6), (0, 0), (4, 4), (1, 1), (3, 3), (5, 5), (2, 2)], (4, 3): [(7, 7), (4, 4), (6, 6), (2, 2), (0, 0), (1, 1), (5, 5), (3, 3)]}, (13, 3): {(13, 3): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8)]}, (5, 3): {(5, 3): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8)]}, (0, 1): {(0, 1): [(0, 0), (1, 1), (2, 2), (3, 3)], (1, 2): [(2, 2), (0, 0), (1, 1)], (9, 0): [(2, 2), (0, 0), (1, 1)], (10, 1): [(2, 2), (0, 0), (1, 1)], (21, 0): [(2, 2), (1, 1), (0, 0)], (12, 0): [(2, 2), (0, 0), (1, 1)], (8, 1): [(2, 2), (0, 0), (1, 1)], (20, 1): [(2, 2), (0, 0), (1, 1)], (17, 2): [(2, 2), (0, 0), (1, 1)], (5, 0): [(2, 2), (1, 1), (0, 0)], (4, 1): [(2, 2), (0, 0), (1, 1)], (13, 0): [(2, 2), (1, 1), (0, 0)]}, (8, 3): {(8, 3): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13)]}, (7, 0): {(7, 0): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]}, (20, 2): {(20, 2): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8)]}, (6, 1): {(6, 1): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25)], (22, 2): [(24, 24), (18, 18), (23, 23), (21, 21), (6, 6), (19, 19), (11, 11), (9, 9), (15, 15), (20, 20), (5, 5), (10, 10), (0, 0), (1, 1), (22, 22), (16, 16), (7, 7), (17, 17), (12, 12), (4, 4), (2, 2), (8, 8), (3, 3), (13, 13), (14, 14)]}, (5, 7): {(5, 7): [(0, 0), (1, 1), (2, 2)]}, (11, 3): {(11, 3): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25)]}, (21, 3): {(21, 3): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13)]}, (16, 1): {(16, 1): [(0, 0)]}, (0, 6): {(10, 5): [(0, 0), (1, 1)], (8, 5): [(0, 0), (1, 1)], (12, 6): [(0, 0), (1, 1)], (13, 6): [(0, 0), (1, 1)], (0, 6): [(0, 0), (1, 1), (2, 2)], (21, 6): [(0, 0), (1, 1)], (9, 6): [(0, 0), (1, 1)], (5, 8): [(0, 0), (1, 1)]}, (12, 4): {(12, 4): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13)]}, (22, 1): {(22, 1): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)]}, (19, 1): {(19, 1): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25)]}, (5, 2): {(5, 2): [(0, 0), (1, 1), (2, 2), (3, 3)]}, (0, 2): {(9, 2): [(3, 3), (4, 4), (1, 1), (0, 0), (2, 2)], (12, 2): [(3, 3), (4, 4), (1, 1), (2, 2), (0, 0)], (13, 2): [(3, 3), (4, 4), (1, 1), (0, 0), (2, 2)], (0, 2): [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], (5, 5): [(3, 3), (4, 4), (1, 1), (0, 0), (2, 2)]}}
    reorder_inverse = {(16, 6): (16, 6), (12, 1): (12, 1), (13, 4): (13, 4), (15, 1): (15, 1), (21, 6): (0, 6), (8, 5): (0, 6), (5, 8): (0, 6), (4, 0): (1, 1), (9, 0): (0, 1), (5, 5): (0, 2), (16, 3): (16, 3), (12, 6): (0, 6), (17, 2): (0, 1), (14, 1): (14, 1), (0, 4): (0, 4), (1, 1): (1, 1), (8, 2): (8, 2), (4, 5): (1, 4), (9, 3): (9, 3), (6, 0): (6, 0), (11, 0): (11, 0), (16, 0): (0, 0), (16, 5): (16, 5), (0, 1): (0, 1), (3, 1): (3, 1), (13, 0): (0, 1), (18, 0): (18, 0), (20, 3): (20, 3), (21, 2): (9, 3), (2, 1): (2, 1), (9, 4): (9, 4), (5, 1): (1, 3), (10, 3): (1, 0), (12, 2): (0, 2), (13, 3): (13, 3), (7, 1): (7, 1), (15, 0): (15, 0), (20, 0): (20, 0), (21, 5): (0, 5), (4, 1): (0, 1), (5, 4): (5, 4), (10, 4): (0, 5), (16, 4): (16, 4), (17, 1): (17, 1), (13, 6): (0, 6), (0, 5): (0, 5), (1, 0): (1, 0), (22, 0): (3, 0), (8, 3): (8, 3), (9, 2): (0, 2), (6, 1): (6, 1), (5, 7): (5, 7), (11, 3): (11, 3), (16, 1): (16, 1), (12, 4): (12, 4), (19, 1): (19, 1), (0, 2): (0, 2), (1, 3): (1, 3), (3, 0): (3, 0), (8, 0): (0, 0), (18, 1): (18, 1), (21, 1): (1, 3), (5, 0): (0, 1), (10, 0): (1, 1), (12, 3): (0, 3), (13, 2): (0, 2), (20, 1): (0, 1), (1, 4): (1, 4), (21, 4): (21, 4), (4, 2): (0, 0), (9, 6): (0, 6), (5, 3): (5, 3), (10, 5): (0, 6), (7, 0): (7, 0), (12, 0): (0, 1), (17, 0): (17, 0), (13, 5): (0, 5), (0, 6): (0, 6), (22, 1): (22, 1), (8, 4): (0, 5), (9, 1): (1, 3), (5, 6): (0, 5), (11, 2): (11, 2), (10, 6): (4, 4), (16, 2): (16, 2), (12, 5): (0, 5), (17, 3): (17, 3), (14, 0): (14, 0), (19, 0): (3, 0), (0, 3): (0, 3), (1, 2): (0, 1), (22, 2): (6, 1), (8, 1): (0, 1), (4, 4): (4, 4), (11, 1): (11, 1), (0, 0): (0, 0), (21, 0): (0, 1), (10, 1): (0, 1), (13, 1): (0, 0), (20, 2): (20, 2), (21, 3): (21, 3), (2, 0): (2, 0), (4, 3): (1, 0), (9, 5): (0, 5), (5, 2): (5, 2), (10, 2): (0, 0)}
    equivs = [[(16, 1)], [(11, 0)], [(16, 2)], [(16, 3)], [(16, 6)], [(16, 5)], [(16, 4)], [(0, 5), (5, 6), (8, 4), (9, 5), (10, 4), (12, 5), (13, 5), (21, 5)], [(0, 6), (5, 8), (8, 5), (9, 6), (10, 5), (12, 6), (13, 6), (21, 6)], [(4, 4), (10, 6)], [(5, 7)], [(11, 1)], [(21, 4)], [(0, 1), (1, 2), (4, 1), (5, 0), (8, 1), (9, 0), (10, 1), (12, 0), (13, 0), (17, 2), (20, 1), (21, 0)], [(0, 0), (4, 2), (8, 0), (10, 2), (13, 1), (16, 0)], [(5, 2)], [(1, 3), (5, 1), (9, 1), (21, 1)], [(1, 4), (4, 5)], [(2, 0)], [(6, 0)], [(7, 0)], [(11, 2)], [(12, 1)], [(14, 0)], [(18, 0)], [(0, 2), (5, 5), (9, 2), (12, 2), (13, 2)], [(3, 0), (19, 0), (22, 0)], [(0, 3), (12, 3)], [(1, 0), (4, 3), (10, 3)], [(5, 3)], [(8, 2)], [(9, 3), (21, 2)], [(13, 3)], [(17, 3)], [(20, 2)], [(15, 0)], [(22, 1)], [(0, 4)], [(1, 1), (4, 0), (10, 0)], [(5, 4)], [(8, 3)], [(9, 4)], [(12, 4)], [(13, 4)], [(17, 1)], [(20, 3)], [(21, 3)], [(2, 1)], [(3, 1)], [(6, 1), (22, 2)], [(7, 1)], [(11, 3)], [(14, 1)], [(15, 1)], [(17, 0)], [(18, 1)], [(19, 1)], [(20, 0)]]
    dirList = ['/home/nicholas/marin-sample/poll-77.png', '/home/nicholas/marin-sample/poll-31.png', '/home/nicholas/marin-sample/poll-06.png', '/home/nicholas/marin-sample/vbm-60.png', '/home/nicholas/marin-sample/poll-87.png', '/home/nicholas/marin-sample/poll-55.png', '/home/nicholas/marin-sample/vbm-22.png', '/home/nicholas/marin-sample/vbm-90.png', '/home/nicholas/marin-sample/mail-65.png', '/home/nicholas/marin-sample/poll-19.png', '/home/nicholas/marin-sample/poll-97.png', '/home/nicholas/marin-sample/poll-66.png', '/home/nicholas/marin-sample/mail-23.png', '/home/nicholas/marin-sample/mail-73.png', '/home/nicholas/marin-sample/vbm-96.png', '/home/nicholas/marin-sample/vbm-10.png', '/home/nicholas/marin-sample/vbm-85.png', '/home/nicholas/marin-sample/poll-42.png', '/home/nicholas/marin-sample/vbm-34.png', '/home/nicholas/marin-sample/vbm-74.png', '/home/nicholas/marin-sample/mail-00.png', '/home/nicholas/marin-sample/mail-53.png', '/home/nicholas/marin-sample/vbm-46.png']
    app = wx.App()
    frame = wx.Frame (None, -1, 'Test', size=(1024, 768))
    VerifyContestGrouping(frame, dirList, equivs, reorder, reorder_inverse, mapping, mapping_inverse)
    frame.Show()
    app.MainLoop()

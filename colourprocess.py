'''
Last updated by An Ting,Hu at 2020.03.08
'''
from numpy import transpose, dot, divide, power, add, array

Minv_XYZ2sRGB = [[3.24, -1.54, -0.50], [-0.97, 1.88, 0.04], [0.06, -0.20, 1.06]]
Minv_XYZ2AdobeRGB = [[2.04, -0.56, -0.34], [-0.97, 1.88, 0.042], [0.013, -0.12, 1.02]]

sGamma = 1 / 2.2
#aGamma = 1 / 2.2
'''
色彩轉換模組
    負責處理色彩空間轉換
'''
class Colour:
    def __init__(self):
        self.CMF_2 = None
        self.CMF_10 = None
        
    '''-----------------------------------------------------------------------------------------------------------------------
    計算輸入頻譜(380~780 波段,Spectra)之三刺激值
    Input:
        Spectra : 頻譜資訊
        Degree : 2 / 10 度視角
        
    Output & Save:
        三刺激值
    '''
    def sd2xyz(self, Spectra, Degree = 2, Inverse = False):
        if Degree == 2:
            return 683 * dot(self.CMF_2, Spectra)
        
        elif Degree == 10:
            return 683 * dot(self.CMF_10, Spectra)
        
    '''
    XYZ to CIELAB
    Input:
        XYZ : 要轉換的色彩XYZ
        XYZw : 參考白XYZ
        
    Output & Save:
        CIE LAB
    '''
    def xyz2lab(self, XYZ, XYZw):
        XYZdiv = divide(XYZ, XYZw)
        
        fXYZ = power(XYZdiv, 1/3)
        fXYZ[XYZdiv < 0.008856] = add(7.787 * XYZdiv[XYZdiv < 0.008856], 16 / 116)
        
        
        # l =116fY-16
        L = 116 * fXYZ[1] - 16
        # a* = 500(fX-fY)
        a = 500 * (fXYZ[0] - fXYZ[1])
        # b* = 200(fY-fZ)
        b = 200 * (fXYZ[1] - fXYZ[2])
        
        return array([L, a, b])
    
    '''
    XYZ to Yxy
    Input:
        XYZ : 要轉換的色彩XYZ
        XYZw : 參考白XYZ
        
    Output & Save:
        Yxy
    '''
    def xyz2Yxy(self, XYZ, XYZw):
        X = XYZ[0]
        Y = XYZ[1]
        Z = XYZ[2]
        
        
        if X == 0 and Y == 0 and Z == 0:
            X = XYZw[0]
            Y = XYZw[1]
            Z = XYZw[2]
            
            return array([0, X / (X + Y + Z) , Y / (X + Y + Z)])
        
        return array([Y, X / (X + Y + Z) , Y / (X + Y + Z)])
    
    '''
    XYZ to RGB(未裁切的0~255)
    Input:
        XYZ : 要轉換的色彩XYZ
        
    Output & Save:
        RGB
    '''
    def xyz2rgb(self, XYZ):
        RGB = dot(transpose(XYZ), transpose(Minv_XYZ2sRGB))
        RGB[RGB < 0] = 0
        RGB = power(RGB, sGamma)
        RGB = RGB * 255
        return RGB
    
    '''
    白平衡 (0~255)
    Input:
        RGB : 參考白、不含激發、含激發
        
    Output & Save:
        RGB : 參考白、不含激發、含激發
    '''
    def awb(self, sRGB_RefW, sRGB_Reflect, sRGB_Mix):
        Rmod = sRGB_RefW[1] / sRGB_RefW[0]
        Gmod = 1
        Bmod = sRGB_RefW[1] / sRGB_RefW[2]
        
        ModFactor = [Rmod, Gmod, Bmod]
        
        sRGB_Reflect = sRGB_Reflect * ModFactor
        sRGB_Mix = sRGB_Mix * ModFactor
        sRGB_RefW = sRGB_RefW * ModFactor
        
        Maximum = max(max(sRGB_Reflect), max(sRGB_Mix), max(sRGB_RefW))
        
        if Maximum > 255:
            # clipping 讓他更粉紅
            sRGB_RefW[sRGB_RefW < 0] = 0
            sRGB_RefW[sRGB_RefW > 255] = 255
            
            sRGB_Reflect[sRGB_Reflect < 0] = 0
            sRGB_Reflect[sRGB_Reflect > 255] = 255
            
            sRGB_Mix[sRGB_Mix < 0] = 0
            sRGB_Mix[sRGB_Mix > 255] = 255
            
            return sRGB_RefW, sRGB_Reflect, sRGB_Mix
            #return sRGB_RefW / Maximum * 255, sRGB_Reflect / Maximum * 255, sRGB_Mix / Maximum * 255
        
        else:
            return sRGB_RefW, sRGB_Reflect, sRGB_Mix
        
    '''-----------------------------------------------------------------------------------------------------------------------
    裁減至區間
    Input:
        Orig : 源陣列
        Upper : 上界
        Lower : 下界
        
    Output & Save:
        Orig : 經修改的陣列
    '''
    def intoRange(self, Orig, Upper = None, Lower = None):
        if Upper != None:
            Orig[Orig > Upper] = Upper
        if Lower != None:
            Orig[Orig < Lower] = Lower
            

        return Orig
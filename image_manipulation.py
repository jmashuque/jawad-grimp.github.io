from PIL import Image, ImageOps, ImageFilter

#------------------------------------------------------------------------------#
#MISC FUNCTIONS----------------------------------------------------------------#
#------------------------------------------------------------------------------#

def eye_dropper(pic, x, y):
    '''Returns the RGB value of the pixel.'''
    
    return pic.getpixel((x, y))

#------------------------------------------------------------------------------#
#IMAGE FUNCTIONS---------------------------------------------------------------#
#------------------------------------------------------------------------------#

def crop_pic(pic, co_list):
    '''Crops the image using the coordinates of top-left and bottom-right pixels
    and returns the modified picture.'''
    
    pic = pic.crop(co_list)
    return pic

#------------------------------------------------------------------------------#

def flip_pic(pic, dir):
    '''Flips the picture and returns the modified picture. dir is 0 or 1
    for horizontal or vertical flipping.'''
    
    pic = pic.transpose(Image.FLIP_TOP_BOTTOM if dir else Image.FLIP_LEFT_RIGHT)
    return pic

#------------------------------------------------------------------------------#

def rotate_pic(pic, angle):
    '''Rotates the picture given an angle. Positive angles are rotated left,
    negative are rotated right.'''
    
    pic = pic.rotate(angle)
    return pic

#------------------------------------------------------------------------------#

def equalize_pic(pic, co_list = 0):
    '''Returns a equalized version of the picture. If co_list is passed, then
    only that part of image is equalized.'''
    
    if co_list != 0:
        x, y = co_list[0], co_list[1]
        temp_pic = pic.crop(co_list)
        temp_pic = ImageOps.equalize(temp_pic)
        pic.paste(temp_pic, (x, y))
    else:
        pic = ImageOps.equalize(pic)
    return pic

#------------------------------------------------------------------------------#

def greyscale_pic(pic, co_list = 0):
    '''Returns a greyscaled version of the picture. If co_list is passed, then
    only that part of image is greyscaled.'''
    
    if co_list != 0:
        x, y = co_list[0], co_list[1]
        temp_pic = pic.crop(co_list)
        temp_pic = ImageOps.grayscale(temp_pic)
        pic.paste(temp_pic, (x, y))
    else:
        pic = ImageOps.grayscale(pic)
    return pic

#------------------------------------------------------------------------------#

def invert_pic(pic, co_list = 0):
    '''Returns a inverted version of the picture. If co_list is passed, then
    only that part of image is inverted.'''
    
    if co_list != 0:
        x, y = co_list[0], co_list[1]
        temp_pic = pic.crop(co_list)
        temp_pic = ImageOps.invert(temp_pic)
        pic.paste(temp_pic, (x, y))
    else:
        pic = ImageOps.invert(pic)
    return pic

#------------------------------------------------------------------------------#
#FILTER FUNCTIONS--------------------------------------------------------------#
#------------------------------------------------------------------------------#

def auto_contrast_pic(pic, co_list = 0):
    '''Normalize image contrast and returns the modified image.'''
    
    if co_list != 0:
        x, y = co_list[0], co_list[1]
        temp_pic = pic.crop(co_list)
        temp_pic = ImageOps.autocontrast(temp_pic, 0)
        pic.paste(temp_pic, (x, y))
    else:
        pic = ImageOps.autocontrast(pic, 0)
    return pic

#------------------------------------------------------------------------------#

def blur_pic(pic, co_list = 0):
    '''Returns a blurred version of the picture. If co_list is passed, then
    only that part of image is blurred.'''
    
    if co_list != 0:
        x, y = co_list[0], co_list[1]
        temp_pic = pic.crop(co_list)
        temp_pic = temp_pic.filter(ImageFilter.BLUR)
        pic.paste(temp_pic, (x, y))
    else:
        pic = pic.filter(ImageFilter.BLUR)
    return pic

#------------------------------------------------------------------------------#

def contour_pic(pic, co_list = 0):
    '''Returns a contoured version of the picture. If co_list is passed, then
    only that part of image is contoured.'''
    
    if co_list != 0:
        x, y = co_list[0], co_list[1]
        temp_pic = pic.crop(co_list)
        temp_pic = temp_pic.filter(ImageFilter.CONTOUR)
        pic.paste(temp_pic, (x, y))
    else:
        pic = pic.filter(ImageFilter.CONTOUR)
    return pic

#------------------------------------------------------------------------------#

def emboss_pic(pic, co_list = 0):
    '''Returns an embossed picture. If co_list is passed, then
    only that part of image is embossed.'''
    
    if co_list != 0:
        x, y = co_list[0], co_list[1]
        temp_pic = pic.crop(co_list)
        temp_pic = temp_pic.filter(ImageFilter.EMBOSS)
        pic.paste(temp_pic, (x, y))
    else:
        pic = pic.filter(ImageFilter.EMBOSS)
    return pic

#------------------------------------------------------------------------------#

def edges_pic(pic, co_list = 0):
    '''Returns a picture with edges highlighted. If co_list is passed, then
    only that part of image is modified.'''
    
    if co_list != 0:
        x, y = co_list[0], co_list[1]
        temp_pic = pic.crop(co_list)
        temp_pic = temp_pic.filter(ImageFilter.FIND_EDGES)
        pic.paste(temp_pic, (x, y))
    else:
        pic = pic.filter(ImageFilter.FIND_EDGES)
    return pic

#------------------------------------------------------------------------------#

def mirror_pic(pic, dir):
    '''Returns a picture with horizontal or vertical mirrors halfway through.
    Direction is 0 or 1 for horizontal or vertical mirroring.'''
    
    if dir == 0:
        x, y = pic.size
        midpoint = x / 2
        mirror_pic = pic.crop((0, 0, midpoint, y))
        mirror_pic = mirror_pic.transpose(Image.FLIP_LEFT_RIGHT)
        pic.paste(mirror_pic, (midpoint, 0))
        
    elif dir == 1:
        x, y = pic.size
        midpoint = y / 2
        mirror_pic = pic.crop((0, 0, x, midpoint))
        mirror_pic = mirror_pic.transpose(Image.FLIP_TOP_BOTTOM)
        pic.paste(mirror_pic, (0, midpoint))
    return pic

#------------------------------------------------------------------------------#

def red_eye_basic(pic):
    '''Given a picture this replaces the red value of pixels with too much red
    by their luminance and returns the modified picture, this uses a complex
    algorithm considered a standard for red eye reduction.'''
    
    pixels = pic.load()
    size = pic.size
    a, b = size[0] - 1, size[1] - 1
    
    for row in range(a):
        for column in range(b):
            (red, green, blue) = pixels[row, column]
            #checks to see if the red value of the pixels is high
            #takes into account red eye can also be purple
            if red > green * 1.15 and red > blue * 0.85:
                red_mod = int(0.89 * green + 0.17 * blue)
                pixels[row, column] = (red_mod, green, blue)
    return pic
    
#------------------------------------------------------------------------------#

def red_eye(pic, co_list = 0):
    '''Uses red_eye_basic funtion to remove redeye effect. If the user has 
    selected part of a picture then the function will only modify the selected
    area.'''
    
    if co_list != 0:
        x, y = co_list[0], co_list[1]
        temp_pic = pic.crop(co_list).crop()
        temp_pic = red_eye_basic(temp_pic)        
        pic.paste(temp_pic, (x,y))
    else:
        pic = red_eye_basic(pic)
    return pic

#------------------------------------------------------------------------------#

def sharpen_pic(pic, co_list = 0):
    '''Returns a picture with shaper changes. If co_list is passed, then
    only that part of image is modified.'''
    
    if co_list != 0:
        x, y = co_list[0], co_list[1]
        temp_pic = pic.crop(co_list)
        temp_pic = temp_pic.filter(ImageFilter.SHARPEN)
        pic.paste(temp_pic, (x, y))
    else:
        pic = pic.filter(ImageFilter.SHARPEN)
    return pic

#------------------------------------------------------------------------------#

def smooth_pic(pic, co_list = 0):
    '''Returns a picture with smoother changes. If co_list is passed, then
    only that part of image is modified.'''
    
    if co_list != 0:
        x, y = co_list[0], co_list[1]
        temp_pic = pic.crop(co_list)
        temp_pic = temp_pic.filter(ImageFilter.SMOOTH)
        pic.paste(temp_pic, (x, y))
    else:
        pic = pic.filter(ImageFilter.SMOOTH)
    return pic
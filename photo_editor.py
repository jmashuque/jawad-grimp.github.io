from Tkinter import *
import image_manipulation 
import tkMessageBox, tkFileDialog, zipfile, StringIO
from PIL import Image, ImageTk

#------------------------------------------------------------------------------#
#MISC FUNCTIONS----------------------------------------------------------------#
#------------------------------------------------------------------------------#

def zip_parser():
    '''Reads all contents of zip files to memory, storing files as PhotoImage.
    '''
    
    file = zipfile.ZipFile('donotunzip.zip')
    for name in file.namelist():
        img = Image.open(StringIO.StringIO(file.read(name)))
        files[name] = ImageTk.PhotoImage(img)

#------------------------------------------------------------------------------#

def mouse_in_image(c_x, c_y):
    '''Checks if mouse is inside canvas image bounds and returns result.'''
    
    return c_x in range(0, image.size[x]) and c_y in range(0, image.size[y])

#------------------------------------------------------------------------------#

def box_not_used():
    '''Checks if selection rectangle has been used.'''
    
    global start, end
    
    return start == (0, 0) and end == (0, 0)

#------------------------------------------------------------------------------#

def gui_close():
    '''Resets variables, discards current image, and disables GUI.'''
    
    global location, image, changes
    
    location = ''
    image = Image.new('RGB', (0, 0))
    update_title()
    state_app(0)
    reset_box()
    changes = 0
    update_image()

#------------------------------------------------------------------------------#

def reset_box():
    '''Resets the coordinates of the selection rectangle and hides it.'''
    
    global start, end
    
    start = end = (0, 0)
    canvas.itemconfig(box, state = HIDDEN)

#------------------------------------------------------------------------------#

def rotatef(win, dir, deg):
    '''Rotates the image with the specifications and displays it.'''
    
    global image
    
    win.destroy()
    update_menu(0)
    image = f.rotate_pic(image, dir * deg)
    update_menu(1)

#------------------------------------------------------------------------------#
#TOGGLE FUNCTIONS--------------------------------------------------------------#
#------------------------------------------------------------------------------#

def toggle_menu(state, entry):
    '''Toggles state of specified menu entries in a given menu.'''
    
    for item in entry:
        for subitem in entry[item]:
            item.entryconfig(subitem, state = NORMAL if state else DISABLED)

#------------------------------------------------------------------------------#

def toggle_button(state, entry):
    '''Toggles state of given buttons.'''
    
    for item in entry:
        item.config(state = NORMAL if state else DISABLED)

#------------------------------------------------------------------------------#
#STATE FUNCTIONS---------------------------------------------------------------#
#------------------------------------------------------------------------------#

def state_app(option):
    '''Changes state of GUI and attributed tools, events, etc.'''
    
    #toggles event entries
    if option:
        canvas.bind('<Motion>', lambda event: event_mouse(event, 1)) #mouse x,y
        canvas.bind('<B1-Motion>', event_mouse)
        canvas.bind('<Leave>', event_mouse)
        b0.bind('<Enter>', lambda event: event_button(event, 0))
        b0.bind('<Leave>', lambda event: event_button(event, 0))
        b1.bind('<Enter>', lambda event: event_button(event, 1))
        b1.bind('<Leave>', lambda event: event_button(event, 1))
        toggle_menu(1, {filemenu: (2, 3, 4), imagemenu: (0, 1, 2, 4, 5, 6), \
                        filtermenu: range(9)}) #menu and tools
        toggle_button(1, (b0, b1))
        state_select(0) #disables active tools
        state_eye(0)
    else:
        canvas.unbind('<Motion>')
        canvas.unbind('<B1-Motion>')
        canvas.unbind('<Leave>')
        b0.unbind('<Enter>')
        b0.unbind('<Leave>')
        b1.unbind('<Enter>')
        b1.unbind('<Leave>')
        toggle_menu(0, {filemenu: (2, 3, 4), editmenu: (0, 1), \
                        imagemenu: (0, 1, 2, 4, 5, 6), filtermenu: range(9)})
        toggle_button(0, (b0, b1))
        state_select(0) #disables active tools
        state_eye(0)

#------------------------------------------------------------------------------#

def state_select(option):
    '''Changes state of selection tool, and turns off other active tools.'''
    
    if option:
        b0.config(relief = SUNKEN)
        reset_box() #resets selection rectangle
        canvas.bind('<Button-1>', event_select)
        canvas.bind('<ButtonRelease-1>', event_select)
    else:
        b0.config(relief = RAISED)
        canvas.unbind('<Button-1>')
        canvas.unbind('<ButtonRelease-1>')
    #turn off eye tool
    if b1.cget('relief') == SUNKEN:
        state_eye(0)

#------------------------------------------------------------------------------#

def state_eye(option):
    '''Changes state of eyedropper tool, and turns off other active tools.'''
    
    global bgdef
    
    if option:
        b1.config(relief = SUNKEN)
        canvas.bind('<Button-1>', event_eye)
    else:
        b1.config(relief = RAISED)
        canvas.unbind('<Button-1>')
        #remove data
        cbox.config(bg = bgdef)
        cstrvar.set('')
    #turn off select tool
    if b0.cget('relief') == SUNKEN:
        state_select(0)

#------------------------------------------------------------------------------#
#EVENT FUNCTIONS---------------------------------------------------------------#
#------------------------------------------------------------------------------#

def event_mouse(event, flag = 0):
    '''Tracks mouse motion inside image and updates to status bar, flag checks
    if event is mouse motion or button pressed mouse motion and is used for
    redirecting event to other event functions.'''
    
    #window coords converted to canvas coords
    c_x, c_y = int(canvas.canvasx(event.x)), int(canvas.canvasy(event.y))
    if mouse_in_image(c_x, c_y) and event.type is '6':
        coordsvar.set(str(c_x) + ',' + str(c_y))
    else:
        coordsvar.set('')
    if (event.type is '8' or event.type is '6') and not flag \
       and b0.cget('relief') == SUNKEN:
        event_select(event) #sends b0 motion to selection tool

#------------------------------------------------------------------------------#

def event_select(event):
    '''Draws a selection rectangle in event dimensions and updates dimensions
    to status bar.'''
    
    global start, end
    
    #coordinates shifted to canvas relative position
    c_x, c_y = int(canvas.canvasx(event.x)), int(canvas.canvasy(event.y))
    if b0.cget('relief') == SUNKEN:
        if event.type is '4': #button pressed
            box_pressed(c_x, c_y)
        elif event.type is '6' or event.type is '8': #movement
            box_moved(c_x, c_y)
        else: #button released
            box_released(c_x, c_y)

#------------------------------------------------------------------------------#

def event_eye(event):
    '''Gets colour of pixel where event occurred.'''
    
    c_x, c_y = int(canvas.canvasx(event.x)), int(canvas.canvasy(event.y))
    if mouse_in_image(c_x, c_y):
        rgb = f.eye_dropper(image, c_x, c_y)
        cbox.config(bg = '#%02x%02x%02x' %(rgb[0], rgb[1], rgb[2])) #hex colour
        cstrvar.set('R:%d\nG:%d\nB:%d' %(rgb[0], rgb[1], rgb[2]))

#------------------------------------------------------------------------------#

def event_button(event, button):
    '''Prints help information for buttons.'''
    
    if event.type is '7':
        helpvar.set('Select a pixel to get its colour values.'\
                    if button else 'Select an area on the screen modify.')
    else:
        helpvar.set('')

#------------------------------------------------------------------------------#
#BOX FUNCTIONS-----------------------------------------------------------------#
#------------------------------------------------------------------------------#

def box_pressed(c_x, c_y):
    '''Starts box drawing once event at given positions falls inside image.'''
    
    global start
    
    if mouse_in_image(c_x, c_y):
        start = c_x, c_y
        canvas.itemconfig(box, state = NORMAL)
        canvas.coords(box, start[x], start[y], start[x], start[y])
    else:
        canvas.itemconfig(box, state = HIDDEN)

#------------------------------------------------------------------------------#

def box_moved(c_x, c_y):
    '''Updates box positions while given positions are changing.'''
    
    global end
    
    #box x-coords
    if max(c_x, 0) > 0:
        if min(c_x, image.size[x]) < image.size[x]:
            end_x = c_x #mouse is in image horizontally
        else:
            end_x = image.size[x] #mouse is right of image
    else:
        end_x = 0 #mouse is left of image
    
    #box y-coords
    if max(c_y, 0) > 0:
        if min(c_y, image.size[y]) < image.size[y]:
            end_y = c_y #mouse is in image vertically
        else:
            end_y = image.size[y] #mouse is below image
    else:
        end_y = 0 #mouse is above image
    
    #updates box
    end = end_x, end_y
    dimensionsvar.set(str(abs(start[x] - end[x])) + 'x' + \
                      str(abs(start[y] - end[y])))
    #box is drawn with equalized coords, but start and end cannot be equalized
    canvas.coords(box, min(start[x], end[x]), min(start[y], end[y]), \
                  max(start[x], end[x]) - 1, max(start[y], end[y]) - 1)

#------------------------------------------------------------------------------#

def box_released(c_x, c_y):
    '''Stops tracking mouse events and finalizes box.'''
    
    global start, end
    
    state_select(0) #disables tool
    dimensionsvar.set('')
    if start != (c_x, c_y): #if mouse was dragged
        #equalized to start < end since values no longer needed for comparison
        start, end = (min(start[x], end[x]), min(start[y], end[y])), \
             (max(start[x], end[x]), max(start[y], end[y]))
        canvas.coords(box, start[x], start[y], end[x] - 1, end[y] - 1)
    else:
        start = (0, 0) #reset coords
        end = (0, 0)
        canvas.itemconfig(box, state = HIDDEN)

#------------------------------------------------------------------------------#
#BUTTON FUNCTIONS--------------------------------------------------------------#
#------------------------------------------------------------------------------#

def button_select():
    '''Enables/disables all functions for the selection rectangle tool.'''
    
    if b0.cget('relief') == RAISED:
        state_select(1)
    else:
        state_select(0)

#------------------------------------------------------------------------------#

def button_eye():
    '''Enables/disables all functions for the eyedropper tool.'''
    
    if b1.cget('relief') == RAISED:
        state_eye(1)
    else:
        state_eye(0)

#------------------------------------------------------------------------------#
#UPDATE FUNCTIONS--------------------------------------------------------------#
#------------------------------------------------------------------------------#

def update_menu(option):
    '''Updates the undo entry and the image after an image operation.'''
    
    global changes, image_rec
    
    if option:
        changes = 1
        update_image()
    else:
        image_rec = image.copy() #removes aliasing caused by paste
        toggle_menu(1, {editmenu: (0,)})
        toggle_menu(0, {editmenu: (1,)})

#------------------------------------------------------------------------------#

def update_title():
    '''Updates title of GUI based on file name.'''
    
    if location == '':
        window.title('The GRIMP')
    else:
        window.title(location.split('/')[-1] + ' - The GRIMP')

#------------------------------------------------------------------------------#

def update_image():
    '''Updates image after its opened, and displays it in the canvas.'''
    
    photo = ImageTk.PhotoImage(image)
    canvas.itemconfig(display, image = photo)
    canvas.config(scrollregion = (0, 0, image.size[x], image.size[y]))
    mainloop() #forces GUI to refresh

#------------------------------------------------------------------------------#

def update_scrollx(min, max):
    '''Updates hor scroller and hides it when not needed.'''
    
    if float(min) <= 0 and float(max) >= 1:
        scrollx.grid_remove()
    else:
        scrollx.grid()
    scrollx.set(min, max)

#------------------------------------------------------------------------------#

def update_scrolly(min, max):
    '''Updates ver scroller and hides it when not needed.'''
    
    if float(min) <= 0 and float(max) >= 1:
        scrolly.grid_remove()
    else:
        scrolly.grid()
    scrolly.set(min, max)

#------------------------------------------------------------------------------#
#MENU FUNCTIONS----------------------------------------------------------------#
#------------------------------------------------------------------------------#

def menu_open():
    '''Prompts user for a picture file, then updates GUI accordingly. This 
    program cannot work with certain greyscale and interlaced formats, and will
    raise a silent error.'''
    
    global location, image, changes
    
    if changes: #checks if current file modified and unsaved
        menu_close(0)
    location = tkFileDialog.askopenfilename(filetypes = [('Picture Files',
                                                          '*.bmp;*.gif;*.jpg;'
                                                          '*.jpeg;*.jpe;*.png;'
                                                          '*.tif;*.tiff')])
    image = Image.open(location)
    if image.mode == 'P': #resolves issue with GIF compatibility
        image = image.convert('RGB')
    update_title()
    changes = 0 #resets changes check
    state_app(1) #enables GUI
    toggle_menu(0, {editmenu: (0, 1)}) #disables previous undo/redos
    reset_box() #resets the selection rectangle in case it was active
    update_image()

#------------------------------------------------------------------------------#

def menu_close(mode):
    '''Prompts user to save if updated without saving, then disables GUI. If
    mode is 0 then menu_open accessed menu_close, therefore gui_close is
    skipped.'''
    
    global changes
    
    if changes:
        option = tkMessageBox.askquestion('The GRIMP',
                                          'Do you want to save changes?',
                                          type=tkMessageBox.YESNOCANCEL)
        if option == 'yes':
            menu_save()
            if mode:
                gui_close()
        elif option == 'no' and mode:
            gui_close()
    elif mode:
        gui_close()

#------------------------------------------------------------------------------#

def menu_save():
    '''Saves current image to last file.'''
    
    global image, location, changes    
    
    changes = 0
    #for BMP compatibility for L, LA, and P modes
    if image.mode != 'RGB' and location[-3:] in \
       ('jpg', 'jpeg', 'jpe', 'bmp', 'gif'):
        image = image.convert('RGB') #will lose transparency and some other data
    image.save(location)

#------------------------------------------------------------------------------#

def menu_save_as():
    '''Saves current image to user selected file.'''
    
    global image, location, changes
    
    location = tkFileDialog.asksaveasfilename(filetypes =
                                              [('BMP','*.bmp'),
                                               ('GIF','*.gif'),
                                               ('JPEG', '*.jpg;*.jpeg;*.jpe'),
                                               ('PNG', '*.png'),
                                               ('TIFF', '*.tif;*.tiff')],
                                              defaultextension='*.bmp',
                                              initialfile = location \
                                              .split('/')[-1].split('.')[0])
    changes = 0
    if image.mode != 'RGB' and location[-3:] in \
       ('jpg', 'jpeg', 'jpe', 'bmp', 'gif'):
        image = image.convert('RGB')
    image.save(location)
    update_title()

#------------------------------------------------------------------------------#

def menu_exit():
    '''Prompts user to save if updated without saving, then terminates.'''
    
    global changes
    
    if changes:
        option = tkMessageBox.askquestion('The GRIMP',
                                          'Do you want to save changes?',
                                          type=tkMessageBox.YESNOCANCEL)
        if option == 'yes':
            menu_save()
            window.destroy()
        elif option == 'no':
            window.destroy()
    else:
        window.destroy()

#------------------------------------------------------------------------------#

def menu_undo():
    '''Restores image to last version prior to undo, and enables undo.'''
    
    global image_rec, image
    
    toggle_menu(0, {editmenu: (0,)})
    toggle_menu(1, {editmenu: (1,)})
    image_rec, image = image, image_rec
    update_menu(1) #updates GUI

#------------------------------------------------------------------------------#

def menu_redo():
    '''Restores image to last version prior to redo.'''
    
    global image_rec, image
    
    toggle_menu(1, {editmenu: (0,)})
    toggle_menu(0, {editmenu: (1,)})
    image_rec, image = image, image_rec
    update_menu(1)

#------------------------------------------------------------------------------#

def menu_crop():
    '''Crops an image based on what the user selected.'''
    
    global image
    
    if not box_not_used():
        update_menu(0) #creates an undo point
        image = f.crop_pic(image, start + end)
        reset_box()
        update_menu(1)

#------------------------------------------------------------------------------#

def menu_flip(mode):
    '''Flips the image based on the mode of flipping (hor/ver).'''
    
    global image
    
    update_menu(0)
    image = f.flip_pic(image, mode)
    update_menu(1)

#------------------------------------------------------------------------------#

def menu_rotate():
    '''Gets degree and rotation direction from user.'''
    
    rotate = Toplevel()
    rotate.iconbitmap('grimp.ico')
    rotate.title('Rotate')
    rotate.resizable(0, 0)
    rotdir = IntVar()
    rotdeg = IntVar()
    rframe = Frame(rotate, bd = 1, relief = GROOVE)
    Radiobutton(rframe, text = 'Left', variable = rotdir, value = 1) \
               .grid(sticky = W)
    Radiobutton(rframe, text = 'Right', variable = rotdir, value = -1) \
               .grid(row = 0, column = 1, sticky = W)
    Radiobutton(rframe, text = '90°', variable = rotdeg, value = 90) \
               .grid(sticky = W)
    Radiobutton(rframe, text = '180°', variable = rotdeg, value = 180) \
               .grid(row = 1, column = 1, sticky = W)
    Radiobutton(rframe, text = '270°', variable = rotdeg, value = 270) \
               .grid(row = 1, column = 2, sticky = W)
    rframe.grid(sticky = W, columnspan = 2, padx = 4, pady = 4)
    Button(rotate, text = 'OK', command = lambda: \
           rotatef(rotate, rotdir.get(), rotdeg.get()), width = 6) \
          .grid(pady = 4)
    Button(rotate, text = 'Cancel', command = rotate.destroy, width = 6) \
          .grid(row = 1, column = 1, pady = 4)
    rotdir.set(1)
    rotdeg.set(90)

#------------------------------------------------------------------------------#

def menu_equalize():
    '''Equalizes an image or part of it and displays it.'''
    
    global image
    
    update_menu(0)
    if box_not_used():
        image = f.equalize_pic(image)
    else:
        image = f.equalize_pic(image, start + end)
        reset_box()
    update_menu(1)

#------------------------------------------------------------------------------#

def menu_greyscale():
    '''Converts image or part of image to greyscale and displays it.'''
    
    global image
    
    update_menu(0)
    if box_not_used():
        image = f.greyscale_pic(image)
    else:
        image = f.greyscale_pic(image, start + end)
        reset_box()
    update_menu(1)

#------------------------------------------------------------------------------#

def menu_invert():
    '''Converts image or part of image to inverted colours and displays it.'''
    
    global image
    
    update_menu(0)
    if box_not_used():
        image = f.invert_pic(image)
    else:
        image = f.invert_pic(image, start + end)
        reset_box()
    update_menu(1)

#------------------------------------------------------------------------------#

def menu_acontrast():
    '''Increases contrast on low contrast or dark images and displays. This
    function does not affect images with acceptable levels of contrast. This
    function also cannot be applied repeatedly.'''
    
    global image
    
    update_menu(0)
    if box_not_used():
        image = f.auto_contrast_pic(image)
    else:
        image = f.auto_contrast_pic(image, start + end)
        reset_box()
    update_menu(1)

#------------------------------------------------------------------------------#

def menu_blur():
    '''Partially blurs open image or part of it and displays it.'''
    
    global image
    
    update_menu(0)
    if box_not_used():
        image = f.blur_pic(image)
    else:
        image = f.blur_pic(image, start + end)
        reset_box()
    update_menu(1)

#------------------------------------------------------------------------------#

def menu_contour():
    '''Creates a contour of the open image or part of it and displays it.'''
    
    global image
    
    update_menu(0)
    if box_not_used():
        image = f.contour_pic(image)
    else:
        image = f.contour_pic(image, start + end)
        reset_box()
    update_menu(1)

#------------------------------------------------------------------------------#

def menu_emboss():
    '''Embosses open image or part of it and displays it.'''
    
    global image
    
    update_menu(0)
    if box_not_used():
        image = f.emboss_pic(image)
    else:
        image = f.emboss_pic(image, start + end)
        reset_box()
    update_menu(1)

#------------------------------------------------------------------------------#

def menu_edges():
    '''Sharpens edges of image or part of it and displays it.'''
    
    global image
    
    update_menu(0)
    if box_not_used():
        image = f.edges_pic(image)
    else:
        image = f.edges_pic(image, start + end)
        reset_box()
    update_menu(1)

#------------------------------------------------------------------------------#

def menu_mirror(mode):
    '''Inserts a horizontal or vertical flip of the image onto the position.'''
    
    global image
    
    update_menu(0)
    image = f.mirror_pic(image, mode)
    update_menu(1)

#------------------------------------------------------------------------------#

def menu_redeye():
    '''Lowers red amount from part of image or whole image.'''
    
    global image
    
    update_menu(0)
    if box_not_used():
        image = f.red_eye(image)
    else:
        image = f.red_eye(image, start + end)
        reset_box()
    update_menu(1)

#------------------------------------------------------------------------------#

def menu_sharpen():
    '''Sharpens image or part of it and displays it.'''
    
    global image
    
    update_menu(0)
    if box_not_used():
        image = f.sharpen_pic(image)
    else:
        image = f.sharpen_pic(image, start + end)
        reset_box()
    update_menu(1)

#------------------------------------------------------------------------------#

def menu_smooth():
    '''Smoothes image or part of it and displays it.'''
    
    global image
    
    update_menu(0)
    if box_not_used():
        image = f.smooth_pic(image)
    else:
        image = f.smooth_pic(image, start + end)
        reset_box()
    update_menu(1)

#------------------------------------------------------------------------------#

def menu_about():
    '''Provides information about the application.'''
    
    about = Toplevel()
    about.iconbitmap('grimp.ico')
    about.overrideredirect(1) #no window
    #centers window on screen
    about.geometry('560x225+%d+%d' %(about.winfo_screenwidth() / 2 - 560 / 2, \
                                     about.winfo_screenheight() / 2 - 255 /2))
    about.title('About The GRIMP')
    about.bind('<Button-1>', lambda x: about.destroy()) #exit by click
    Label(about, image = files['p0.png']).pack()

#------------------------------------------------------------------------------#
#DEREFERENCED GLOBAL VARIABLES-------------------------------------------------#
#------------------------------------------------------------------------------#

changes = 0 #tracks file changes not saved
location = '' #location of open file
image = Image.new('RGB', (0, 0)) #image file being modified
image_rec = Image.new('RGB', (0, 0)) #for redo and undo
x, y = 0, 1 #for easier reading
start = 0, 0 #for selection box
end = 0, 0
files = {} #storage for files
f = image_manipulation #alias

#------------------------------------------------------------------------------#
#MAIN--------------------------------------------------------------------------#
#------------------------------------------------------------------------------#

if __name__ == '__main__':
    #WINDOW
    window = Tk()
    window.protocol('WM_DELETE_WINDOW', menu_exit) #catches x button
    window.minsize(400, 310) #minimum resize allowed
    window.wm_state('zoomed') #starts maximized, required for alignmet
    window.iconbitmap('grimp.ico') #app icon
    
    zip_parser() #loads files to memory
    
    #MENU BAR
    menubar = Menu(window)
    window.config(menu = menubar)
    filemenu = Menu(menubar, tearoff = 0) #tearoff removes annoying dashes
    editmenu = Menu(menubar, tearoff = 0)
    imagemenu = Menu(menubar, tearoff = 0)
    flipmenu = Menu(imagemenu, tearoff = 0)
    filtermenu = Menu(menubar, tearoff = 0)
    mirrormenu = Menu(filtermenu, tearoff = 0)
    helpmenu = Menu(menubar, tearoff = 0)
    
    #file menu
    filemenu.add_command(label = 'Open...', command = menu_open)
    filemenu.add_separator()
    filemenu.add_command(label = 'Close', command = lambda: menu_close(1))
    filemenu.add_command(label = 'Save', command = menu_save)
    filemenu.add_command(label = 'Save As...', command = menu_save_as)
    filemenu.add_separator()
    filemenu.add_command(label = 'Exit', command = menu_exit)
    menubar.add_cascade(label = 'File', menu = filemenu)
    #edit menu
    editmenu.add_command(label = 'Undo', command = menu_undo)
    editmenu.add_command(label = 'Redo', command = menu_redo)
    menubar.add_cascade(label = 'Edit', menu = editmenu)
    #image menu
    imagemenu.add_command(label = 'Crop', command = menu_crop)
    flipmenu.add_command(label = 'Horizontally', command = lambda: menu_flip(0))
    flipmenu.add_command(label = 'Vertically', command = lambda: menu_flip(1))
    imagemenu.add_cascade(label = 'Flip', menu = flipmenu)
    imagemenu.add_command(label = 'Rotate...', command = menu_rotate)
    imagemenu.add_separator()
    imagemenu.add_command(label = 'Equalize', command = menu_equalize)
    imagemenu.add_command(label = 'Greyscale', command = menu_greyscale)
    imagemenu.add_command(label = 'Invert', command = menu_invert)
    menubar.add_cascade(label = 'Image', menu = imagemenu)
    #filter menu
    filtermenu.add_command(label = 'Auto Contrast', command = menu_acontrast)
    filtermenu.add_command(label = 'Blur', command = menu_blur)
    filtermenu.add_command(label = 'Contour', command = menu_contour)
    filtermenu.add_command(label = 'Emboss', command = menu_emboss)
    filtermenu.add_command(label = 'Find Edges', command = menu_edges)
    mirrormenu.add_command(label = 'Horizontally', command = \
                           lambda: menu_mirror(0))
    mirrormenu.add_command(label = 'Vertically', command = \
                           lambda: menu_mirror(1))
    filtermenu.add_cascade(label = 'Mirror', menu = mirrormenu)
    filtermenu.add_command(label = 'Remove Red Eye', command = menu_redeye)
    filtermenu.add_command(label = 'Sharpen', command = menu_sharpen)
    filtermenu.add_command(label = 'Smooth', command = menu_smooth)
    menubar.add_cascade(label = 'Filter', menu = filtermenu)
    #help menu
    helpmenu.add_command(label = 'About', command = menu_about)
    menubar.add_cascade(label = 'Help', menu = helpmenu)
    
    #CONTAINER
    container = Frame(window, relief = GROOVE, bd = 1)
    container.pack(fill = BOTH, expand = 1)
    
    #TOOL BAR
    toolbar = Frame(container, bd = 1, relief = RIDGE)
    
    cstrvar = StringVar() #eyedropper value
    bgdef = toolbar.cget('bg') #default background colour
    
    #logo
    Label(toolbar, image = files['p1.png']).pack()
    #buttons
    b0 = Button(toolbar, image = files['b0.png'], bd = 1, \
                command = button_select)
    b0.pack() #selection tool
    b1 = Button(toolbar, image = files['b1.png'], bd = 1, \
                command = button_eye)
    b1.pack() #eyedropper tool
    #eyedropper data
    cbox = Label(toolbar, bd = 1, height = 2, relief = SUNKEN)
    cbox.pack(fill = X, pady = 2, padx = 2)
    Label(toolbar, textvariable = cstrvar).pack()
    toolbar.pack(side = LEFT, fill = Y)
    
    #IMAGE AREA
    imagearea = Frame(container)
    imagearea.pack(side = LEFT, fill = BOTH, expand = 1)
    imagearea.columnconfigure(0, weight = 1)
    imagearea.rowconfigure(0, weight = 1)
    
    #vertical scroll bar
    scrolly = Scrollbar(imagearea)
    scrolly.grid(row = 0, column = 1, sticky = N+S)
    #horizontal scroll bar
    scrollx = Scrollbar(imagearea, orient = HORIZONTAL)
    scrollx.grid(sticky = W+E)
    
    #CANVAS
    canvas = Canvas(imagearea, yscrollcommand = update_scrolly,
                    xscrollcommand = update_scrollx)
    canvas.grid(row = 0, sticky = W+E+N+S)
    
    #display for image
    display = canvas.create_image(0, 0, anchor = NW)
    #selection rectangle for selection tool
    box = canvas.create_rectangle(0, 0, 0, 0, state = HIDDEN, dash = (7, 7))
    
    #scroll functions
    scrolly.config(command = canvas.yview)
    scrollx.config(command = canvas.xview)
    
    #STATUS BAR
    status = Frame(window)
    status.pack(fill = X, side = BOTTOM)
    status.columnconfigure(0, weight = 1)
    status.columnconfigure(1, minsize = 100)
    status.columnconfigure(2, minsize = 100)
    
    #label variables
    helpvar = StringVar()
    coordsvar = StringVar()
    dimensionsvar = StringVar()
    
    #help
    Label(status, textvariable = helpvar, anchor = W, bd = 1, relief = \
          GROOVE).grid(sticky = W+E)
    #coordinates
    Label(status, textvariable = coordsvar, anchor = W, bd = 1, relief = \
          GROOVE).grid(row = 0, column = 1, sticky = W+E)
    #dimensions
    Label(status, textvariable = dimensionsvar, anchor = W, bd = 1, relief = \
          GROOVE).grid(row = 0, column = 2, sticky = W+E)
    
    #SETTINGS
    state_app(0) #disables GUI
    update_title()
    
    mainloop()
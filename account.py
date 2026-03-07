import pygame 
import sys 
import cv2 
from database import init_database ,get_or_create_user ,get_top_scores ,get_user 
from utils import Button ,fade_in ,fade_out ,BUTTON_WIDTH ,BUTTON_HEIGHT ,BUTTON_SPACING 


ACCENT =(182 ,233 ,17 )
BG =(14 ,14 ,18 )
BG2 =(22 ,22 ,28 )
GRAY =(110 ,110 ,115 )
WHITE =(220 ,220 ,220 )
GOLD =(255 ,200 ,50 )
SILVER =(190 ,190 ,200 )
BRONZE =(195 ,140 ,80 )

_current_user =None 

def get_current_user ():
    return _current_user 

def set_current_user (user ):
    global _current_user 
    _current_user =user 

def clear_current_user ():
    global _current_user 
    _current_user =None 





class TextInput :
    def __init__ (self ,x ,y ,width ,height ,font ,max_length =3 ):
        self .x =x ;self .y =y 
        self .width =width ;self .height =height 
        self .font =font 
        self .text =""
        self .active =False 
        self .disabled =False 
        self .max_length =max_length 
        self .rect =pygame .Rect (x ,y ,width ,height )
        self .cursor_timer =0 

    def handle_event (self ,event ):
        if self .disabled :
            return None 
        if event .type ==pygame .MOUSEBUTTONDOWN :
            self .active =self .rect .collidepoint (event .pos )
        if event .type ==pygame .KEYDOWN and self .active :
            if event .key ==pygame .K_BACKSPACE :
                self .text =self .text [:-1 ]
            elif event .key in (pygame .K_RETURN ,pygame .K_KP_ENTER ):
                return "enter"
            elif event .unicode and event .unicode .isalnum ()and len (self .text )<self .max_length :
                self .text +=event .unicode .upper ()
        return None 

    def draw (self ,surface ):
        self .rect =pygame .Rect (self .x ,self .y ,self .width ,self .height )
        surf =pygame .Surface ((self .width ,self .height ),pygame .SRCALPHA )

        if self .disabled :
            pygame .draw .rect (surf ,(*BG ,180 ),(0 ,0 ,self .width ,self .height ),border_radius =4 )
            pygame .draw .rect (surf ,(*GRAY ,160 ),(0 ,0 ,self .width ,self .height ),2 ,border_radius =4 )
        else :
            pygame .draw .rect (surf ,(*BG ,210 ),(0 ,0 ,self .width ,self .height ),border_radius =4 )
            border =ACCENT if self .active else (*ACCENT [:3 ],120 )
            pygame .draw .rect (surf ,border ,(0 ,0 ,self .width ,self .height ),2 ,border_radius =4 )

        surface .blit (surf ,(self .x ,self .y ))

        txt_col =GRAY if self .disabled else ACCENT 
        txt_surf =self .font .render (self .text ,True ,txt_col )
        ty =self .y +(self .height -txt_surf .get_height ())//2 
        surface .blit (txt_surf ,(self .x +12 ,ty ))

        if self .active and not self .disabled :
            self .cursor_timer =(self .cursor_timer +1 )%60 
            if self .cursor_timer <30 :
                cx =self .x +12 +txt_surf .get_width ()+2 
                pygame .draw .line (surface ,ACCENT ,(cx ,ty ),(cx ,ty +txt_surf .get_height ()),2 )





def draw_login_card (screen ,font ,x ,y ,width ,current_user ):
    """Рисует карточку входа или профиля. Возвращает (высота_карточки, y_под_полем_ввода)."""
    P =24 
    TITLE_FONT =pygame .font .Font (None ,38 )
    LBL_FONT =pygame .font .Font (None ,26 )


    if current_user :
        name ,total ,easy ,medium ,hard =current_user 
        rows =[("Лёгкий",easy ),("Средний",medium ),("Сложный",hard )]
        ROW_H =38 
        card_h =P +40 +12 +1 +16 +ROW_H *len (rows )+16 +1 +16 +ROW_H +P 

        surf =pygame .Surface ((width ,card_h ),pygame .SRCALPHA )
        pygame .draw .rect (surf ,(*BG ,245 ),(0 ,0 ,width ,card_h ),border_radius =8 )
        pygame .draw .rect (surf ,ACCENT ,(0 ,0 ,width ,card_h ),2 ,border_radius =8 )


        title =TITLE_FONT .render (f"ОХОТНИК: {name}",True ,ACCENT )
        surf .blit (title ,((width -title .get_width ())//2 ,P ))
        line_y =P +title .get_height ()+12 
        pygame .draw .line (surf ,(*ACCENT ,80 ),(P ,line_y ),(width -P ,line_y ),1 )

        cy =line_y +16 
        for label ,score in rows :
            lbl =LBL_FONT .render (label ,True ,GRAY )
            val =LBL_FONT .render (str (score ),True ,WHITE )
            surf .blit (lbl ,(P ,cy +(ROW_H -lbl .get_height ())//2 ))
            surf .blit (val ,(width -P -val .get_width (),cy +(ROW_H -val .get_height ())//2 ))
            pygame .draw .line (surf ,(35 ,37 ,42 ),
            (P ,cy +ROW_H -1 ),(width -P ,cy +ROW_H -1 ),1 )
            cy +=ROW_H 


        cy +=16 
        pygame .draw .line (surf ,(*ACCENT ,80 ),(P ,cy -1 ),(width -P ,cy -1 ),1 )
        cy +=16 
        tot_f =pygame .font .Font (None ,34 )
        tl =tot_f .render ("Итого",True ,ACCENT )
        tv =tot_f .render (str (total ),True ,ACCENT )
        surf .blit (tl ,(P ,cy +(ROW_H -tl .get_height ())//2 ))
        surf .blit (tv ,(width -P -tv .get_width (),cy +(ROW_H -tv .get_height ())//2 ))

        screen .blit (surf ,(x ,y ))
        return card_h ,None 


    INPUT_H =46 
    INPUT_W =width -P *2 
    card_h =P +40 +12 +1 +20 +22 +10 +INPUT_H +20 +BUTTON_HEIGHT +P +14 +32 +P //2 

    surf =pygame .Surface ((width ,card_h ),pygame .SRCALPHA )
    pygame .draw .rect (surf ,(*BG ,245 ),(0 ,0 ,width ,card_h ),border_radius =8 )
    pygame .draw .rect (surf ,ACCENT ,(0 ,0 ,width ,card_h ),2 ,border_radius =8 )

    title =TITLE_FONT .render ("ВХОД В MELODY HUNT",True ,ACCENT )
    surf .blit (title ,((width -title .get_width ())//2 ,P ))
    line_y =P +title .get_height ()+12 
    pygame .draw .line (surf ,(*ACCENT ,80 ),(P ,line_y ),(width -P ,line_y ),1 )

    screen .blit (surf ,(x ,y ))

    input_y_abs =y +line_y +1 +20 +22 +10 
    return card_h ,input_y_abs 


def draw_hint (screen ,x ,y ,width ):
    """Подсказка 'Войдите чтобы сохранить результаты' под карточкой."""
    f =pygame .font .Font (None ,22 )
    lines =["Войдите в аккаунт,","чтобы сохранить результаты"]
    LINE_H =f .get_height ()
    P =12 
    h =P *2 +LINE_H *2 +6 
    surf =pygame .Surface ((width ,h ),pygame .SRCALPHA )
    pygame .draw .rect (surf ,(*BG ,200 ),(0 ,0 ,width ,h ),border_radius =8 )
    pygame .draw .rect (surf ,(*GRAY ,80 ),(0 ,0 ,width ,h ),1 ,border_radius =8 )
    for i ,line in enumerate (lines ):
        lbl =f .render (line ,True ,GRAY )
        surf .blit (lbl ,((width -lbl .get_width ())//2 ,P +i *(LINE_H +6 )))
    screen .blit (surf ,(x ,y ))





def draw_scores_table (screen ,font ,x ,y ,width ,height ,current_user =None ,max_rows =10 ):
    scores =get_top_scores (limit =max_rows )
    current_name =current_user [0 ]if current_user else None 

    P =18 
    ROW_H =36 
    HFONT =pygame .font .Font (None ,26 )
    TFONT =pygame .font .Font (None ,40 )
    RFONT =pygame .font .Font (None ,26 )

    surf =pygame .Surface ((width ,height ),pygame .SRCALPHA )
    pygame .draw .rect (surf ,(*BG ,245 ),(0 ,0 ,width ,height ),border_radius =8 )
    pygame .draw .rect (surf ,ACCENT ,(0 ,0 ,width ,height ),2 ,border_radius =8 )


    title =TFONT .render ("ТАБЛИЦА ЛИДЕРОВ",True ,ACCENT )
    surf .blit (title ,((width -title .get_width ())//2 ,P ))
    line_y =P +title .get_height ()+10 
    pygame .draw .line (surf ,(*ACCENT ,80 ),(P ,line_y ),(width -P ,line_y ),1 )


    COL_NUM =36 
    COL_NAME =120 
    COL_SCORES =(width -P *2 -COL_NUM -COL_NAME )//4 
    col_xs =[
    P ,
    P +COL_NUM ,
    P +COL_NUM +COL_NAME ,
    P +COL_NUM +COL_NAME +COL_SCORES ,
    P +COL_NUM +COL_NAME +COL_SCORES *2 ,
    P +COL_NUM +COL_NAME +COL_SCORES *3 ,
    ]
    col_ws =[COL_NUM ,COL_NAME ,COL_SCORES ,COL_SCORES ,COL_SCORES ,COL_SCORES ]

    headers =["#","Имя","Всего","Лёгкий","Средний","Сложный"]
    header_y =line_y +12 

    for i ,(hdr ,cx ,cw )in enumerate (zip (headers ,col_xs ,col_ws )):
        h =HFONT .render (hdr ,True ,ACCENT )
        surf .blit (h ,(cx +(cw -h .get_width ())//2 ,header_y ))

    sep_y =header_y +HFONT .get_height ()+8 
    pygame .draw .line (surf ,(*ACCENT ,60 ),(P ,sep_y ),(width -P ,sep_y ),1 )


    content_y =sep_y +8 
    if not scores :
        ph =HFONT .render ("Пока нет записей",True ,GRAY )
        surf .blit (ph ,((width -ph .get_width ())//2 ,
        content_y +(height -content_y )//2 ))
    else :
        medal_colors =[GOLD ,SILVER ,BRONZE ]
        for idx ,row in enumerate (scores ):
            name ,total ,easy ,medium ,hard =row 
            ry =content_y +idx *ROW_H 

            if ry +ROW_H >height -P :
                break 


            is_me =(name ==current_name )
            if is_me :
                row_bg =(*ACCENT ,18 )
            elif idx %2 ==0 :
                row_bg =(*BG2 ,120 )
            else :
                row_bg =(0 ,0 ,0 ,0 )

            if row_bg [3 ]>0 :
                pygame .draw .rect (surf ,row_bg ,
                (P ,ry ,width -P *2 ,ROW_H ),border_radius =3 )


            if is_me :
                txt_col =ACCENT 
            elif idx <3 :
                txt_col =medal_colors [idx ]
            else :
                txt_col =WHITE 

            values =[str (idx +1 ),name ,str (total ),str (easy ),str (medium ),str (hard )]
            for vi ,(val ,cx ,cw )in enumerate (zip (values ,col_xs ,col_ws )):
                v =RFONT .render (val ,True ,txt_col )
                surf .blit (v ,(cx +(cw -v .get_width ())//2 ,
                ry +(ROW_H -v .get_height ())//2 ))


            if idx <len (scores )-1 :
                pygame .draw .line (surf ,(35 ,37 ,42 ),
                (P ,ry +ROW_H -1 ),(width -P ,ry +ROW_H -1 ),1 )

    screen .blit (surf ,(x ,y ))





def account_screen (screen ,clock ,fps ,Button ,BUTTON_WIDTH ,BUTTON_HEIGHT ,
BUTTON_SPACING ,SCREEN_WIDTH ,SCREEN_HEIGHT ,font ,cap ):
    init_database ()
    global _current_user 


    background_path ="resources/menu/BackStatic.png"
    try :
        background_image =pygame .transform .scale (
        pygame .image .load (background_path ),(SCREEN_WIDTH ,SCREEN_HEIGHT ))
        background_loaded =True 
    except :
        background_loaded =False 
        background_image =None 


    LOGO_PATH ="resources/menu/melodyhuntlogo.png"
    LOGO_X =SCREEN_WIDTH //2 
    LOGO_Y =8 
    LOGO_SCALE =0.4 
    try :
        logo_image =pygame .image .load (LOGO_PATH )
        logo_image =pygame .transform .scale (logo_image ,(
        int (logo_image .get_width ()*LOGO_SCALE ),
        int (logo_image .get_height ()*LOGO_SCALE )))
        logo_loaded =True 
    except :
        logo_loaded =False 
        logo_image =None 



    PANEL_H =460 
    CARD_W =360 
    TABLE_W =680 
    GAP =40 
    TOTAL_W =CARD_W +GAP +TABLE_W 
    START_X =(SCREEN_WIDTH -TOTAL_W )//2 
    PANELS_Y =SCREEN_HEIGHT //2 -PANEL_H //2 +20 

    card_x =START_X 
    table_x =START_X +CARD_W +GAP 


    P =24 
    INPUT_W =CARD_W -P *2 
    INPUT_H =46 

    text_input =TextInput (card_x +P ,PANELS_Y +120 ,INPUT_W ,INPUT_H ,font ,max_length =3 )
    if _current_user :
        text_input .disabled =True 


    BTN_W =180 
    login_button =Button (
    card_x +(CARD_W -BTN_W )//2 ,
    PANELS_Y +200 ,
    BTN_W ,BUTTON_HEIGHT ,
    "Выйти"if _current_user else "Войти",
    font )


    back_button =Button (
    SCREEN_WIDTH //2 -BUTTON_WIDTH //2 ,
    SCREEN_HEIGHT -BUTTON_HEIGHT -40 ,
    BUTTON_WIDTH ,BUTTON_HEIGHT ,"Назад",font )

    def draw_account_frame (mouse_pos ,dt ):

        cap .read ()
        if background_loaded :
            screen .blit (background_image ,(0 ,0 ))
        else :
            screen .fill ((0 ,0 ,0 ))


        if logo_loaded :
            lx =LOGO_X -logo_image .get_width ()//2 
            screen .blit (logo_image ,(lx ,LOGO_Y ))


        if _current_user :
            status_text =f"Добро пожаловать, {_current_user[0]}."
        else :
            status_text ="Вы не авторизованы"
        screen .blit (font .render (status_text ,True ,ACCENT ),(50 ,50 ))


        fresh_user =get_user (_current_user [0 ])if _current_user else None 
        card_h ,input_y_abs =draw_login_card (screen ,font ,card_x ,PANELS_Y ,CARD_W ,fresh_user )

        if not _current_user :

            lbl_font =pygame .font .Font (None ,26 )
            lbl =lbl_font .render ("Введите имя (3 символа)",True ,GRAY )
            lbl_y =PANELS_Y +76 +12 +20 
            screen .blit (lbl ,(card_x +(CARD_W -lbl .get_width ())//2 ,lbl_y ))


            text_input .disabled =False 
            text_input .x =card_x +P 
            text_input .y =lbl_y +lbl .get_height ()+10 
            text_input .rect =pygame .Rect (text_input .x ,text_input .y ,INPUT_W ,INPUT_H )
            text_input .draw (screen )


            login_button .text ="Войти"
            login_button .x =card_x +(CARD_W -BTN_W )//2 
            login_button .y =text_input .y +INPUT_H +20 
            login_button .check_hover (mouse_pos )
            login_button .update_animation (dt )
            login_button .draw (screen )


            draw_hint (screen ,card_x ,PANELS_Y +card_h +8 ,CARD_W )
        else :

            login_button .text ="Выйти"
            login_button .x =card_x +(CARD_W -BTN_W )//2 
            login_button .y =PANELS_Y +card_h +12 
            login_button .check_hover (mouse_pos )
            login_button .update_animation (dt )
            login_button .draw (screen )


        draw_scores_table (screen ,font ,table_x ,PANELS_Y ,TABLE_W ,PANEL_H ,
        current_user =fresh_user ,max_rows =10 )


        back_button .check_hover (mouse_pos )
        back_button .update_animation (dt )
        back_button .draw (screen )

    def draw_account ():
        draw_account_frame (pygame .mouse .get_pos (),0.016 )

    if not fade_in (screen ,clock ,fps ,draw_account ,SCREEN_WIDTH ,SCREEN_HEIGHT ,duration =0.3 ):
        return "quit"

    running =True 
    while running :
        dt =min (clock .tick (fps )/1000.0 ,0.1 )
        mp =pygame .mouse .get_pos ()

        for event in pygame .event .get ():
            if event .type ==pygame .QUIT :
                return "quit"

            elif event .type ==pygame .KEYDOWN :
                if event .key ==pygame .K_ESCAPE :
                    if fade_out (screen ,clock ,fps ,draw_account ,SCREEN_WIDTH ,SCREEN_HEIGHT ,0.3 ):
                        return "main_menu"
                elif not _current_user :
                    result =text_input .handle_event (event )
                    if result =="enter"and text_input .text :
                        _current_user =get_or_create_user (text_input .text )
                        text_input .text =""
                        text_input .disabled =True 

            elif event .type ==pygame .MOUSEBUTTONDOWN and event .button ==1 :
                if not _current_user :
                    text_input .handle_event (event )

                if back_button .is_clicked (mp ):
                    if fade_out (screen ,clock ,fps ,draw_account ,SCREEN_WIDTH ,SCREEN_HEIGHT ,0.3 ):
                        return "main_menu"

                elif login_button .is_clicked (mp ):
                    if _current_user :
                        _current_user =None 
                        text_input .text =""
                        text_input .disabled =False 
                        text_input .active =False 
                    elif text_input .text :
                        _current_user =get_or_create_user (text_input .text )
                        text_input .text =""
                        text_input .disabled =True 
                        text_input .active =False 

        draw_account_frame (mp ,dt )
        pygame .display .flip ()

    return "quit"

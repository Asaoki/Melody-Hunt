import pygame 
import cv2 
import numpy as np 
import sys 
from account import account_screen ,get_current_user 
from game import game_screen 
from settings import SettingsMenu 
from utils import (Button ,fade_in ,fade_out ,lerp_color ,
BUTTON_WIDTH ,BUTTON_HEIGHT ,BUTTON_SPACING ,
BUTTON_COLOR ,BUTTON_HOVER_COLOR ,BUTTON_TEXT_COLOR ,
BUTTON_TEXT_HOVER_COLOR ,BUTTON_BORDER_COLOR ,
BUTTON_BORDER_WIDTH ,BUTTON_ALPHA ,BUTTON_ANIMATION_SPEED )


pygame .init ()
pygame .mixer .init ()


screen_info =pygame .display .Info ()
SCREEN_WIDTH =screen_info .current_w 
SCREEN_HEIGHT =screen_info .current_h 


screen =pygame .display .set_mode ((SCREEN_WIDTH ,SCREEN_HEIGHT ),pygame .FULLSCREEN )
pygame .display .set_caption ("Melody Hunt")


video_path ="resources/menu/background.mp4"
cap =cv2 .VideoCapture (video_path )


audio_path ="resources/menu/excess-instrumental.ogg"
try :
    pygame .mixer .music .load (audio_path )
    audio_loaded =True 
except Exception as e :
    print (f"Предупреждение: не удалось загрузить аудиофайл: {e}")
    audio_loaded =False 


LOGO_PATH ="resources/menu/melodyhuntlogo.png"
LOGO_X =SCREEN_WIDTH //2 
LOGO_Y =8 
LOGO_SCALE =0.4 


try :
    logo_image =pygame .image .load (LOGO_PATH )

    if LOGO_SCALE !=1.0 :
        original_size =logo_image .get_size ()
        new_size =(int (original_size [0 ]*LOGO_SCALE ),int (original_size [1 ]*LOGO_SCALE ))
        logo_image =pygame .transform .scale (logo_image ,new_size )
    logo_loaded =True 
except Exception as e :
    print (f"Предупреждение: не удалось загрузить логотип: {e}")
    logo_loaded =False 
    logo_image =None 


fps =cap .get (cv2 .CAP_PROP_FPS )
if fps ==0 :
    fps =30 


clock =pygame .time .Clock ()


running =True 


font =pygame .font .Font (None ,36 )

class DifficultyWindow :
    """Окно выбора уровня сложности"""
    def __init__ (self ,screen_width ,screen_height ,button_class ,button_width ,button_height ,button_spacing ,font ):
        self .screen_width =screen_width 
        self .screen_height =screen_height 
        self .Button =button_class 
        self .button_width =button_width 
        self .button_height =button_height 
        self .button_spacing =button_spacing 
        self .font =font 


        self .window_width =500 
        self .window_height =350 
        self .window_x =(screen_width -self .window_width )//2 
        self .window_y =(screen_height -self .window_height )//2 


        self .bg_color =(30 ,30 ,30 )
        self .border_color =(182 ,233 ,17 )
        self .border_width =3 
        self .alpha =240 


        self .animation_progress =0.0 
        self .animation_speed =5.0 
        self .is_visible =False 


        self .close_button_size =30 
        self .close_button_x =self .window_x +self .window_width -self .close_button_size -10 
        self .close_button_y =self .window_y +10 


        try :
            close_image =pygame .image .load ("resources/menu/close.png")
            self .close_button_image =pygame .transform .scale (close_image ,(self .close_button_size ,self .close_button_size ))
            self .close_button_loaded =True 
        except Exception as e :
            print (f"Предупреждение: не удалось загрузить изображение кнопки закрытия: {e}")
            self .close_button_loaded =False 
            self .close_button_image =None 


        button_start_y =self .window_y +80 
        button_center_x =self .window_x +(self .window_width -button_width )//2 

        self .buttons =[
        self .Button (button_center_x ,button_start_y ,button_width ,button_height ,"Легкий",self .font ),
        self .Button (button_center_x ,button_start_y +button_height +button_spacing ,button_width ,button_height ,"Средний",self .font ),
        self .Button (button_center_x ,button_start_y +(button_height +button_spacing )*2 ,button_width ,button_height ,"Сложный",self .font )
        ]

        self .selected_difficulty =None 
        self .close_button_hovered =False 

    def show (self ):
        """Показывает окно с анимацией"""
        self .is_visible =True 
        self .animation_progress =0.0 
        self .selected_difficulty =None 

    def hide (self ):
        """Скрывает окно"""
        self .is_visible =False 
        self .animation_progress =0.0 
        self .selected_difficulty =None 

    def update (self ,dt ,mouse_pos ):
        """Обновляет состояние окна и анимацию
        dt - время, прошедшее с последнего кадра в секундах
        """
        if not self .is_visible :
            return None 


        if self .animation_progress <1.0 :
            self .animation_progress =min (1.0 ,self .animation_progress +self .animation_speed *dt )


        for button in self .buttons :
            button .check_hover (mouse_pos )
            button .update_animation (dt )


        if self .animation_progress >=0.5 :
            close_rect =pygame .Rect (self .close_button_x ,self .close_button_y ,self .close_button_size ,self .close_button_size )
            self .close_button_hovered =close_rect .collidepoint (mouse_pos )
        else :
            self .close_button_hovered =False 

        return None 

    def handle_click (self ,mouse_pos ):
        """Обрабатывает клики по окну
        Возвращает выбранный уровень сложности или "close" для закрытия окна
        """
        if not self .is_visible or self .animation_progress <0.5 :
            return None 


        close_rect =pygame .Rect (self .close_button_x ,self .close_button_y ,self .close_button_size ,self .close_button_size )
        if close_rect .collidepoint (mouse_pos ):
            self .hide ()
            return "close"


        for button in self .buttons :
            if button .is_clicked (mouse_pos ):
                if button .text =="Легкий":
                    self .selected_difficulty ="easy"
                elif button .text =="Средний":
                    self .selected_difficulty ="medium"
                elif button .text =="Сложный":
                    self .selected_difficulty ="hard"
                return self .selected_difficulty 

        return None 

    def draw (self ,surface ):
        """Отрисовывает окно"""
        if not self .is_visible or self .animation_progress <=0 :
            return 



        t =self .animation_progress 

        ease_t =1 -(1 -t )**3 


        scale =0.7 +(1.0 -0.7 )*ease_t 

        current_alpha =int (self .alpha *ease_t )


        scaled_width =int (self .window_width *scale )
        scaled_height =int (self .window_height *scale )
        scaled_x =self .window_x +(self .window_width -scaled_width )//2 
        scaled_y =self .window_y +(self .window_height -scaled_height )//2 


        window_surface =pygame .Surface ((scaled_width ,scaled_height ),pygame .SRCALPHA )


        bg_color_with_alpha =(*self .bg_color ,current_alpha )
        pygame .draw .rect (window_surface ,bg_color_with_alpha ,(0 ,0 ,scaled_width ,scaled_height ))


        border_color_with_alpha =(*self .border_color ,current_alpha )
        pygame .draw .rect (window_surface ,border_color_with_alpha ,(0 ,0 ,scaled_width ,scaled_height ),self .border_width )


        title_text ="Выберите уровень сложности"

        title_color =(182 ,233 ,17 )
        title_surface =self .font .render (title_text ,True ,title_color )
        title_rect =title_surface .get_rect (center =(scaled_width //2 ,40 ))

        title_with_alpha =pygame .Surface (title_surface .get_size (),pygame .SRCALPHA )
        title_with_alpha .set_alpha (current_alpha )
        title_with_alpha .blit (title_surface ,(0 ,0 ))
        window_surface .blit (title_with_alpha ,title_rect )


        surface .blit (window_surface ,(scaled_x ,scaled_y ))



        for button in self .buttons :
            button .draw (surface )


        if self .close_button_loaded and self .close_button_image :

            close_image_with_alpha =self .close_button_image .copy ()
            close_image_with_alpha .set_alpha (current_alpha )


            if self .close_button_hovered :

                bright_image =close_image_with_alpha .copy ()
                bright_image .fill ((255 ,255 ,255 ,0 ),special_flags =pygame .BLEND_RGBA_ADD )
                bright_image .set_alpha (current_alpha )
                surface .blit (bright_image ,(self .close_button_x ,self .close_button_y ))
            else :
                surface .blit (close_image_with_alpha ,(self .close_button_x ,self .close_button_y ))


class ConfirmExitWindow :
    """Окно подтверждения выхода из главного меню"""

    W =560 
    H =260 
    BG =(14 ,14 ,18 )
    ACCENT =(182 ,233 ,17 )

    def __init__ (self ,screen_width ,screen_height ,button_class ,
    button_width ,button_height ,button_spacing ,font ):
        self .sw =screen_width 
        self .sh =screen_height 
        self .Button =button_class 
        self .font =font 

        self .wx =(screen_width -self .W )//2 
        self .wy =(screen_height -self .H )//2 

        self .animation_progress =0.0 
        self .animation_speed =5.0 
        self .is_visible =False 

        BW =min (button_width ,(self .W -60 )//2 -10 )
        BH =button_height 
        gap =20 
        total =BW *2 +gap 
        left_x =self .wx +(self .W -total )//2 
        btn_y =self .wy +self .H -BH -36 

        self .exit_button =self .Button (left_x ,btn_y ,BW ,BH ,"Выход",font )
        self .stay_button =self .Button (left_x +BW +gap ,btn_y ,BW ,BH ,"Остаться",font )

    def show (self ):
        self .is_visible =True 
        self .animation_progress =0.0 

    def hide (self ):
        self .is_visible =False 
        self .animation_progress =0.0 

    def update (self ,dt ,mouse_pos ):
        if not self .is_visible :
            return 
        self .animation_progress =min (1.0 ,
        self .animation_progress +self .animation_speed *dt )
        if self .animation_progress >=0.5 :
            for btn in (self .exit_button ,self .stay_button ):
                btn .check_hover (mouse_pos )
                btn .update_animation (dt )

    def handle_click (self ,mouse_pos ):
        """Возвращает 'exit' | 'continue' | None"""
        if not self .is_visible or self .animation_progress <0.5 :
            return None 
        if self .exit_button .is_clicked (mouse_pos ):
            self .hide ()
            return "exit"
        if self .stay_button .is_clicked (mouse_pos ):
            self .hide ()
            return "continue"
        return None 

    def draw (self ,surface ):
        if not self .is_visible or self .animation_progress <=0 :
            return 

        t =self .animation_progress 
        ease_t =1 -(1 -t )**3 
        alpha =int (255 *ease_t )
        scale =0.7 +0.3 *ease_t 

        sw =int (self .W *scale )
        sh =int (self .H *scale )
        sx =self .wx +(self .W -sw )//2 
        sy =self .wy +(self .H -sh )//2 


        dim =pygame .Surface ((self .sw ,self .sh ),pygame .SRCALPHA )
        dim .fill ((0 ,0 ,0 ,int (120 *ease_t )))
        surface .blit (dim ,(0 ,0 ))


        panel =pygame .Surface ((sw ,sh ),pygame .SRCALPHA )
        pygame .draw .rect (panel ,(*self .BG ,int (245 *ease_t )),
        (0 ,0 ,sw ,sh ),border_radius =6 )
        pygame .draw .rect (panel ,(*self .ACCENT ,alpha ),
        (0 ,0 ,sw ,sh ),3 ,border_radius =6 )
        line_y =int (sh *0.38 )
        pygame .draw .line (panel ,(*self .ACCENT ,int (80 *ease_t )),
        (20 ,line_y ),(sw -20 ,line_y ),1 )


        f_title =pygame .font .Font (None ,36 )
        title =f_title .render ("Выйти из игры?",True ,self .ACCENT )
        ts =pygame .Surface (title .get_size (),pygame .SRCALPHA )
        ts .set_alpha (alpha )
        ts .blit (title ,(0 ,0 ))
        panel .blit (ts ,((sw -title .get_width ())//2 ,int (sh *0.14 )))


        f_sub =pygame .font .Font (None ,28 )
        sub =f_sub .render ("Вы уверены, что хотите выйти?",True ,(200 ,200 ,200 ))
        ss =pygame .Surface (sub .get_size (),pygame .SRCALPHA )
        ss .set_alpha (alpha )
        ss .blit (sub ,(0 ,0 ))
        panel .blit (ss ,((sw -sub .get_width ())//2 ,int (sh *0.46 )))

        surface .blit (panel ,(sx ,sy ))

        if self .animation_progress >=0.5 :
            self .exit_button .draw (surface )
            self .stay_button .draw (surface )


class MusicPlayer :
    """Боковая панель плеера — выезжает справа по нажатию стрелки"""

    PANEL_WIDTH =380 
    ARROW_W =36 
    ARROW_H =70 
    ROW_H =46 
    PADDING =18 
    ACCENT =(182 ,233 ,17 )
    BG =(14 ,14 ,18 )
    BG_ALPHA =230 
    SCROLL_SPEED =3 

    def __init__ (self ,screen_width ,screen_height ,font ):
        self .sw =screen_width 
        self .sh =screen_height 
        self .font =font 
        self .small_font =pygame .font .Font (None ,26 )


        self .slide =0.0 
        self .target =0.0 
        self .SPEED =7.0 


        self .tracks =[]
        self ._load_tracks ()


        self .current_index =-1 
        self .is_playing =False 
        self .scroll_offset =0 
        self .hovered_index =-1 


        self .arrow_hovered =False 


        self ._sound =None 
        self ._channel =None 
        self ._settings_ref =None 




    def _load_tracks (self ):
        import os 
        exts =('.mp3','.wav','.ogg','.flac','.m4a')
        folders ={
        'easy':'resources/gamemodes/easy',
        'medium':'resources/gamemodes/medium',
        'hard':'resources/gamemodes/hard',
        }
        label_map ={'easy':'Лёгкий','medium':'Средний','hard':'Сложный'}
        seen =set ()
        for key ,folder in folders .items ():
            if not os .path .exists (folder ):
                continue 
            for fname in sorted (os .listdir (folder )):
                if fname .lower ().endswith (exts ):
                    path =os .path .join (folder ,fname )
                    name =os .path .splitext (fname )[0 ]
                    display =name 
                    if path not in seen :
                        seen .add (path )
                        self .tracks .append ((display ,path ))




    @property 
    def panel_x (self ):
        """Левый край панели с учётом анимации слайда"""

        t =1 -(1 -self .slide )**3 
        return int (self .sw -self .PANEL_WIDTH *t )

    @property 
    def arrow_x (self ):
        return self .panel_x -self .ARROW_W 

    @property 
    def arrow_y (self ):
        return self .sh //2 -self .ARROW_H //2 

    @property 
    def arrow_rect (self ):
        return pygame .Rect (self .arrow_x ,self .arrow_y ,self .ARROW_W ,self .ARROW_H )

    @property 
    def is_open (self ):
        return self .target >0.5 




    @property 
    def _header_h (self ):
        return 56 

    @property 
    def _visible_rows (self ):
        available =self .sh -self ._header_h -self .PADDING 
        return max (1 ,available //self .ROW_H )




    def toggle (self ):
        if self .is_open :

            self .stop ()
            self .target =0.0 
        else :
            self .target =1.0 

    def play_track (self ,index ):
        if 0 <=index <len (self .tracks ):
            _ ,path =self .tracks [index ]
            try :

                pygame .mixer .music .set_volume (0.0 )

                if self ._sound :
                    self ._sound .stop ()
                self ._sound =pygame .mixer .Sound (path )
                self ._channel =self ._sound .play (-1 )

                if self ._channel and hasattr (self ,'_settings_ref')and self ._settings_ref :
                    vol =self ._settings_ref .vol_master *self ._settings_ref .vol_music 
                    self ._channel .set_volume (vol )
                self .current_index =index 
                self .is_playing =True 
            except Exception as e :
                print (f"Плеер: не удалось загрузить трек: {e}")
                pygame .mixer .music .set_volume (1.0 )

    def stop (self ):
        if self ._sound :
            self ._sound .stop ()
            self ._sound =None 
            self ._channel =None 

        pygame .mixer .music .set_volume (1.0 )
        self .is_playing =False 
        self .current_index =-1 

    def _clamp_scroll (self ):
        max_scroll =max (0 ,len (self .tracks )-self ._visible_rows )
        self .scroll_offset =max (0 ,min (self .scroll_offset ,max_scroll ))




    def update (self ,dt ,mouse_pos ):

        if self ._channel and self ._settings_ref and self .is_playing :
            vol =self ._settings_ref .vol_master *self ._settings_ref .vol_music 
            self ._channel .set_volume (vol )


        diff =self .target -self .slide 
        if abs (diff )>0.001 :
            self .slide +=diff *self .SPEED *dt 
            self .slide =max (0.0 ,min (1.0 ,self .slide ))
        else :
            self .slide =self .target 


        self .arrow_hovered =self .arrow_rect .collidepoint (mouse_pos )


        self .hovered_index =-1 
        if self .slide >0.3 :
            mx ,my =mouse_pos 
            if mx >=self .panel_x :
                row_area_y =self ._header_h 
                rel_y =my -row_area_y 
                if rel_y >=0 :
                    row =rel_y //self .ROW_H +self .scroll_offset 
                    if 0 <=row <len (self .tracks ):
                        self .hovered_index =row 

    def handle_click (self ,mouse_pos ,menu_music_loaded ):
        """Обрабатывает клик. Возвращает True если клик был поглощён панелью."""
        mx ,my =mouse_pos 


        if self .arrow_rect .collidepoint (mouse_pos ):
            self .toggle ()
            return True 


        if self .slide >0.3 :
            if mx >=self .panel_x :

                row_area_y =self ._header_h 
                rel_y =my -row_area_y 
                if rel_y >=0 :
                    row =rel_y //self .ROW_H +self .scroll_offset 
                    if 0 <=row <len (self .tracks ):
                        if row ==self .current_index and self .is_playing :
                            self .stop ()
                        else :
                            self .play_track (row )
                return True 
            else :

                self .toggle ()
                return True 

        return False 

    def handle_scroll (self ,dy ,mouse_pos ):
        """Обрабатывает колесо мыши. Возвращает True если поглощён."""
        mx ,_ =mouse_pos 
        if self .slide >0.3 and mx >=self .panel_x :
            self .scroll_offset -=dy *self .SCROLL_SPEED 
            self ._clamp_scroll ()
            return True 
        return False 




    def draw (self ,surface ):
        self ._draw_arrow (surface )
        if self .slide >0.01 :
            self ._draw_panel (surface )

    def _draw_arrow (self ,surface ):
        ax ,ay =self .arrow_x ,self .arrow_y 
        aw ,ah =self .ARROW_W ,self .ARROW_H 


        arrow_surf =pygame .Surface ((aw ,ah ),pygame .SRCALPHA )
        bg_alpha =220 if self .arrow_hovered else 180 
        pygame .draw .rect (arrow_surf ,(*self .BG ,bg_alpha ),(0 ,0 ,aw ,ah ))
        border_color =self .ACCENT if self .arrow_hovered else (80 ,80 ,80 )
        pygame .draw .rect (arrow_surf ,border_color ,(0 ,0 ,aw ,ah ),2 )


        cx ,cy =aw //2 ,ah //2 
        size =10 
        if self .is_open :

            pts =[(cx +size ,cy ),(cx -size +4 ,cy -size ),(cx -size +4 ,cy +size )]
        else :

            pts =[(cx -size ,cy ),(cx +size -4 ,cy -size ),(cx +size -4 ,cy +size )]

        arrow_color =self .ACCENT if self .arrow_hovered else (200 ,200 ,200 )
        pygame .draw .polygon (arrow_surf ,arrow_color ,pts )
        surface .blit (arrow_surf ,(ax ,ay ))

    def _draw_panel (self ,surface ):
        pw =self .PANEL_WIDTH 
        ph =self .sh 
        px =self .panel_x 
        t =self .slide 

        panel_surf =pygame .Surface ((pw ,ph ),pygame .SRCALPHA )


        alpha =int (self .BG_ALPHA *t )
        pygame .draw .rect (panel_surf ,(*self .BG ,alpha ),(0 ,0 ,pw ,ph ))


        border_alpha =int (255 *t )
        pygame .draw .line (panel_surf ,(*self .ACCENT ,border_alpha ),(0 ,0 ),(0 ,ph ),3 )


        title_alpha =int (255 *t )
        title_surf =self .font .render ("ПЛЕЕР",True ,self .ACCENT )
        title_with_a =pygame .Surface (title_surf .get_size (),pygame .SRCALPHA )
        title_with_a .set_alpha (title_alpha )
        title_with_a .blit (title_surf ,(0 ,0 ))
        panel_surf .blit (title_with_a ,(self .PADDING ,14 ))


        pygame .draw .line (panel_surf ,(*self .ACCENT ,int (120 *t )),
        (0 ,self ._header_h -4 ),(pw ,self ._header_h -4 ),1 )


        visible =self ._visible_rows 
        for i in range (visible ):
            track_idx =i +self .scroll_offset 
            if track_idx >=len (self .tracks ):
                break 

            display_name ,_ =self .tracks [track_idx ]
            row_y =self ._header_h +i *self .ROW_H 
            is_current =(track_idx ==self .current_index )
            is_hovered =(track_idx ==self .hovered_index )


            if is_current :
                row_bg =(*self .ACCENT ,int (40 *t ))
            elif is_hovered :
                row_bg =(255 ,255 ,255 ,int (18 *t ))
            else :
                row_bg =(0 ,0 ,0 ,0 )

            if row_bg [3 ]>0 :
                pygame .draw .rect (panel_surf ,row_bg ,(0 ,row_y ,pw ,self .ROW_H ))


            if is_current and self .is_playing :
                icon ="▶"
                icon_surf =self .small_font .render (icon ,True ,self .ACCENT )
                icon_a =pygame .Surface (icon_surf .get_size (),pygame .SRCALPHA )
                icon_a .set_alpha (int (255 *t ))
                icon_a .blit (icon_surf ,(0 ,0 ))
                panel_surf .blit (icon_a ,(self .PADDING ,row_y +(self .ROW_H -icon_surf .get_height ())//2 ))
                text_offset =self .PADDING +icon_surf .get_width ()+6 
            else :
                text_offset =self .PADDING 


            text_color =self .ACCENT if is_current else (
            (230 ,230 ,230 )if is_hovered else (170 ,170 ,170 )
            )

            max_w =pw -text_offset -self .PADDING 
            name_surf =self .small_font .render (display_name ,True ,text_color )
            if name_surf .get_width ()>max_w :

                trimmed =display_name 
                while len (trimmed )>1 :
                    trimmed =trimmed [:-1 ]
                    name_surf =self .small_font .render (trimmed +"…",True ,text_color )
                    if name_surf .get_width ()<=max_w :
                        break 

            name_a =pygame .Surface (name_surf .get_size (),pygame .SRCALPHA )
            name_a .set_alpha (int (255 *t ))
            name_a .blit (name_surf ,(0 ,0 ))
            panel_surf .blit (name_a ,(text_offset ,row_y +(self .ROW_H -name_surf .get_height ())//2 ))


            if i <visible -1 :
                pygame .draw .line (panel_surf ,(50 ,50 ,50 ,int (100 *t )),
                (self .PADDING ,row_y +self .ROW_H -1 ),
                (pw -self .PADDING ,row_y +self .ROW_H -1 ),1 )


        if len (self .tracks )>visible :
            sb_x =pw -6 
            sb_h =ph -self ._header_h 
            thumb_h =max (30 ,int (sb_h *visible /len (self .tracks )))
            max_scroll =len (self .tracks )-visible 
            thumb_y =self ._header_h +int ((sb_h -thumb_h )*self .scroll_offset /max (1 ,max_scroll ))
            pygame .draw .rect (panel_surf ,(40 ,40 ,40 ,int (180 *t )),(sb_x ,self ._header_h ,4 ,sb_h ))
            pygame .draw .rect (panel_surf ,(*self .ACCENT ,int (160 *t )),(sb_x ,thumb_y ,4 ,thumb_h ))

        surface .blit (panel_surf ,(px ,0 ))


def resize_frame (frame ,target_width ,target_height ):
    """Изменяет размер кадра видео под размер экрана"""
    frame_height ,frame_width =frame .shape [:2 ]


    scale_w =target_width /frame_width 
    scale_h =target_height /frame_height 
    scale =max (scale_w ,scale_h )

    new_width =int (frame_width *scale )
    new_height =int (frame_height *scale )


    resized =cv2 .resize (frame ,(new_width ,new_height ),interpolation =cv2 .INTER_LINEAR )


    if new_width >target_width or new_height >target_height :
        start_x =(new_width -target_width )//2 
        start_y =(new_height -target_height )//2 
        resized =resized [start_y :start_y +target_height ,start_x :start_x +target_width ]

    return resized 

def draw_main_menu_frame (cap ,buttons ,mouse_pos ,dt ,difficulty_window =None ,music_player =None ,settings_menu =None ,confirm_exit_window =None ):
    """Функция для отрисовки одного кадра главного меню"""

    if difficulty_window is None or not difficulty_window .is_visible :
        for button in buttons :
            button .check_hover (mouse_pos )
            button .update_animation (dt )
    else :

        for button in buttons :
            button .is_hovered =False 

            button .update_animation (dt )


    if difficulty_window :
        difficulty_window .update (dt ,mouse_pos )


    ret ,frame =cap .read ()

    if not ret :

        cap .set (cv2 .CAP_PROP_POS_FRAMES ,0 )
        ret ,frame =cap .read ()
        if not ret :

            screen .fill ((0 ,0 ,0 ))
            if logo_loaded and logo_image :
                logo_rect =logo_image .get_rect ()
                logo_x_pos =LOGO_X -logo_rect .width //2 if LOGO_X ==SCREEN_WIDTH //2 else LOGO_X 
                screen .blit (logo_image ,(logo_x_pos ,LOGO_Y ))


            current_user =get_current_user ()
            status_x =50 
            status_y =50 
            if current_user :
                status_text =f"Добро пожаловать, {current_user[0]}."
            else :
                status_text ="Вы не авторизованы"

            status_surface =font .render (status_text ,True ,(182 ,233 ,17 ))
            screen .blit (status_surface ,(status_x ,status_y ))

            for button in buttons :
                button .draw (screen )


            if difficulty_window :
                difficulty_window .draw (screen )
            return 


    frame =cv2 .cvtColor (frame ,cv2 .COLOR_BGR2RGB )


    frame =resize_frame (frame ,SCREEN_WIDTH ,SCREEN_HEIGHT )


    frame =np .rot90 (frame )
    frame =pygame .surfarray .make_surface (frame )


    screen .blit (frame ,(0 ,0 ))


    if logo_loaded and logo_image :
        logo_rect =logo_image .get_rect ()
        logo_x_pos =LOGO_X -logo_rect .width //2 if LOGO_X ==SCREEN_WIDTH //2 else LOGO_X 
        screen .blit (logo_image ,(logo_x_pos ,LOGO_Y ))


    current_user =get_current_user ()
    status_x =50 
    status_y =50 
    if current_user :
        status_text =f"Добро пожаловать, {current_user[0]}."
    else :
        status_text ="Вы не авторизованы"

    status_surface =font .render (status_text ,True ,(182 ,233 ,17 ))
    screen .blit (status_surface ,(status_x ,status_y ))


    for button in buttons :
        button .draw (screen )


    if difficulty_window :
        difficulty_window .draw (screen )


    if music_player :
        music_player .update (dt ,mouse_pos )


        if music_player .slide >0.01 :
            dim_alpha =int (140 *music_player .slide )
            dim_surf =pygame .Surface ((SCREEN_WIDTH ,SCREEN_HEIGHT ),pygame .SRCALPHA )
            dim_surf .fill ((0 ,0 ,0 ,dim_alpha ))
            screen .blit (dim_surf ,(0 ,0 ))

        music_player .draw (screen )


    if settings_menu :
        settings_menu .update (dt )
        settings_menu .draw (screen ,mouse_pos )


    if confirm_exit_window :
        confirm_exit_window .update (dt ,mouse_pos )
        confirm_exit_window .draw (screen )

def main_menu ():
    global running 


    cap .set (cv2 .CAP_PROP_POS_FRAMES ,0 )


    if audio_loaded :
        if not pygame .mixer .music .get_busy ():
            pygame .mixer .music .play (-1 )





    total_height =(BUTTON_HEIGHT *3 )+(BUTTON_SPACING *2 )
    start_y =(SCREEN_HEIGHT -total_height )//2 +80 

    button_center_x =SCREEN_WIDTH //2 -BUTTON_WIDTH //2 

    buttons =[
    Button (button_center_x ,start_y ,BUTTON_WIDTH ,BUTTON_HEIGHT ,"Начать игру",font ),
    Button (button_center_x ,start_y +BUTTON_HEIGHT +BUTTON_SPACING ,BUTTON_WIDTH ,BUTTON_HEIGHT ,"Аккаунт",font ),
    Button (button_center_x ,start_y +(BUTTON_HEIGHT +BUTTON_SPACING )*2 ,BUTTON_WIDTH ,BUTTON_HEIGHT ,"Выйти",font )
    ]


    difficulty_window =DifficultyWindow (SCREEN_WIDTH ,SCREEN_HEIGHT ,Button ,BUTTON_WIDTH ,BUTTON_HEIGHT ,BUTTON_SPACING ,font )


    music_player =MusicPlayer (SCREEN_WIDTH ,SCREEN_HEIGHT ,font )


    settings_menu =SettingsMenu (SCREEN_WIDTH ,SCREEN_HEIGHT ,
    vol_master =pygame .mixer .music .get_volume (),
    vol_music =1.0 ,vol_sfx =1.0 )
    music_player ._settings_ref =settings_menu 


    confirm_exit_window =ConfirmExitWindow (SCREEN_WIDTH ,SCREEN_HEIGHT ,Button ,
    BUTTON_WIDTH ,BUTTON_HEIGHT ,BUTTON_SPACING ,font )

    while running :

        dt =clock .tick (fps )/1000.0 

        dt =min (dt ,0.1 )

        mouse_pos =pygame .mouse .get_pos ()

        for event in pygame .event .get ():
            if event .type ==pygame .QUIT :
                running =False 


            if settings_menu .handle_event (event ,mouse_pos ):
                continue 


            elif confirm_exit_window .is_visible :
                if event .type ==pygame .MOUSEBUTTONDOWN and event .button ==1 :
                    action =confirm_exit_window .handle_click (mouse_pos )
                    if action =="exit":
                        running =False 


            elif event .type ==pygame .KEYDOWN :
                if event .key ==pygame .K_ESCAPE :
                    if difficulty_window .is_visible :
                        difficulty_window .hide ()
                    else :
                        confirm_exit_window .show ()
            elif event .type ==pygame .MOUSEWHEEL :

                music_player .handle_scroll (event .y ,mouse_pos )

            elif event .type ==pygame .MOUSEBUTTONDOWN :
                if event .button ==1 :

                    if music_player .handle_click (mouse_pos ,audio_loaded ):
                        pass 

                    elif difficulty_window .is_visible :
                        selected_difficulty =difficulty_window .handle_click (mouse_pos )
                        if selected_difficulty =="close":

                            pass 
                        elif selected_difficulty :

                            difficulty_window .hide ()

                            music_player .stop ()
                            music_player .target =0.0 
                            music_player .slide =0.0 
                            if audio_loaded :
                                pygame .mixer .music .stop ()

                            def draw_main_menu ():
                                draw_main_menu_frame (cap ,buttons ,pygame .mouse .get_pos (),0.016 ,difficulty_window ,music_player ,settings_menu ,confirm_exit_window )

                            if fade_out (screen ,clock ,fps ,draw_main_menu ,SCREEN_WIDTH ,SCREEN_HEIGHT ,duration =0.3 ):

                                current_difficulty =selected_difficulty 
                                while True :
                                    result =game_screen (screen ,clock ,fps ,Button ,BUTTON_WIDTH ,BUTTON_HEIGHT ,BUTTON_SPACING ,SCREEN_WIDTH ,SCREEN_HEIGHT ,font ,cap ,difficulty =current_difficulty ,settings_menu =settings_menu )
                                    if result =="quit":
                                        running =False 
                                        break 
                                    elif result and result .startswith ("restart_"):

                                        current_difficulty =result .split ("_",1 )[1 ]

                                        continue 
                                    elif result =="main_menu":

                                        cap .set (cv2 .CAP_PROP_POS_FRAMES ,0 )

                                        if audio_loaded :
                                            pygame .mixer .music .stop ()
                                            pygame .mixer .music .load (audio_path )
                                            pygame .mixer .music .play (-1 )

                                        if not fade_in (screen ,clock ,fps ,draw_main_menu ,SCREEN_WIDTH ,SCREEN_HEIGHT ,duration =0.3 ):
                                            running =False 
                                        break 
                                    else :
                                        break 
                    else :

                        if not music_player .is_open :
                            for button in buttons :
                                if button .is_clicked (mouse_pos ):
                                    if button .text =="Выйти":
                                        confirm_exit_window .show ()
                                    elif button .text =="Начать игру":

                                        difficulty_window .show ()

                                    elif button .text =="Аккаунт":

                                        def draw_main_menu ():
                                            draw_main_menu_frame (cap ,buttons ,pygame .mouse .get_pos (),0.016 ,difficulty_window ,music_player ,settings_menu ,confirm_exit_window )

                                        if fade_out (screen ,clock ,fps ,draw_main_menu ,SCREEN_WIDTH ,SCREEN_HEIGHT ,duration =0.3 ):


                                            result =account_screen (screen ,clock ,fps ,Button ,BUTTON_WIDTH ,BUTTON_HEIGHT ,BUTTON_SPACING ,SCREEN_WIDTH ,SCREEN_HEIGHT ,font ,cap )
                                            if result =="quit":
                                                running =False 
                                            elif result =="main_menu":

                                                if not fade_in (screen ,clock ,fps ,draw_main_menu ,SCREEN_WIDTH ,SCREEN_HEIGHT ,duration =0.3 ):
                                                    running =False 





        draw_main_menu_frame (cap ,buttons ,mouse_pos ,dt ,difficulty_window ,music_player ,settings_menu ,confirm_exit_window )
        pygame .display .flip ()


    if audio_loaded :
        pygame .mixer .music .stop ()


    cap .release ()
    pygame .quit ()
    sys .exit ()

if __name__ =="__main__":
    main_menu ()


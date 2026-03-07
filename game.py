import pygame 
import cv2 
import os 
import random 
from account import get_current_user 
from database import update_best_score ,get_user 
from utils import Button ,fade_in ,fade_out ,BUTTON_WIDTH ,BUTTON_HEIGHT ,BUTTON_SPACING 
from settings import SettingsMenu 
from game_logic import load_songs_from_folder ,build_songs_list ,generate_round ,apply_answer ,SCORE_CORRECT ,SCORE_WRONG 

class ProgressBar :
    """Класс для анимированного прогресс-бара на 15 секунд"""
    def __init__ (self ,x ,y ,width ,height ,duration =15.0 ):
        """
        x, y - позиция прогресс-бара
        width - ширина прогресс-бара
        height - высота прогресс-бара
        duration - длительность анимации в секундах (по умолчанию 15)
        """
        self .x =x 
        self .y =y 
        self .width =width 
        self .height =height 
        self .duration =duration 


        self .progress =0.0 
        self .is_running =False 
        self .start_time =0.0 
        self .elapsed_time =0.0 


        self .bg_color =(50 ,50 ,50 )
        self .bar_color =(182 ,233 ,17 )
        self .border_color =(255 ,255 ,255 )
        self .border_width =2 

    def start (self ):
        """Запускает прогресс-бар (или возобновляет, если был остановлен)"""
        if not self .is_running :
            self .is_running =True 

            current_time =pygame .time .get_ticks ()/1000.0 
            self .start_time =current_time -self .elapsed_time 

    def stop (self ):
        """Останавливает прогресс-бар (прогресс сохраняется)"""
        if self .is_running :
            self .is_running =False 

            current_time =pygame .time .get_ticks ()/1000.0 
            self .elapsed_time =current_time -self .start_time 

    def reset (self ):
        """Сбрасывает прогресс-бар в начальное состояние"""
        self .is_running =False 
        self .progress =0.0 
        self .elapsed_time =0.0 
        self .start_time =0.0 

    def update (self ,dt ):
        """
        Обновляет прогресс-бар
        dt - время, прошедшее с последнего кадра в секундах (не используется, но оставлено для совместимости)
        """
        if self .is_running :

            current_time =pygame .time .get_ticks ()/1000.0 
            self .elapsed_time =current_time -self .start_time 


            self .progress =min (self .elapsed_time /self .duration ,1.0 )


            if self .progress >=1.0 :
                self .is_running =False 
                self .elapsed_time =self .duration 

    def draw (self ,surface ):
        """Отрисовывает прогресс-бар на поверхности"""

        pygame .draw .rect (surface ,self .bg_color ,(self .x ,self .y ,self .width ,self .height ))


        pygame .draw .rect (surface ,self .border_color ,(self .x ,self .y ,self .width ,self .height ),self .border_width )


        filled_width =int (self .width *self .progress )

        if filled_width >0 :

            pygame .draw .rect (surface ,self .bar_color ,(self .x ,self .y ,filled_width ,self .height ))


            if filled_width <self .width :
                pygame .draw .line (surface ,self .border_color ,
                (self .x +filled_width ,self .y ),
                (self .x +filled_width ,self .y +self .height ),2 )

    def get_progress (self ):
        """Возвращает текущий прогресс (0.0 - 1.0)"""
        return self .progress 

    def is_complete (self ):
        """Возвращает True, если прогресс-бар завершен"""
        return self .progress >=1.0 



























class GameOverWindow :
    """Окно завершения игры"""
    def __init__ (self ,screen_width ,screen_height ,button_class ,button_width ,button_height ,button_spacing ,font ):
        self .screen_width =screen_width 
        self .screen_height =screen_height 
        self .Button =button_class 
        self .button_width =button_width 
        self .button_height =button_height 
        self .button_spacing =button_spacing 
        self .font =font 


        self .window_width =600 
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


        button_start_y =self .window_y +160 
        button_center_x =self .window_x +(self .window_width -button_width )//2 

        self .buttons =[
        self .Button (button_center_x ,button_start_y ,button_width ,button_height ,"Повтор",self .font ),
        self .Button (button_center_x ,button_start_y +button_height +button_spacing ,button_width ,button_height ,"Выход",self .font )
        ]

        self .selected_action =None 
        self .final_score =0 

    def show (self ,score ):
        """Показывает окно с анимацией"""
        self .is_visible =True 
        self .animation_progress =0.0 
        self .selected_action =None 
        self .final_score =score 

    def hide (self ):
        """Скрывает окно"""
        self .is_visible =False 
        self .animation_progress =0.0 
        self .selected_action =None 

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

        return None 

    def handle_click (self ,mouse_pos ):
        """Обрабатывает клики по окну
        Возвращает "restart" для повтора, "exit" для выхода, или None
        """
        if not self .is_visible or self .animation_progress <0.5 :
            return None 


        for button in self .buttons :
            if button .is_clicked (mouse_pos ):
                if button .text =="Повтор":
                    self .selected_action ="restart"
                    return "restart"
                elif button .text =="Выход":
                    self .selected_action ="exit"
                    return "exit"

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


        title_text ="Охота за мелодиями окончена"
        title_color =(182 ,233 ,17 )
        title_surface =self .font .render (title_text ,True ,title_color )
        title_rect =title_surface .get_rect (center =(scaled_width //2 ,60 ))

        title_with_alpha =pygame .Surface (title_surface .get_size (),pygame .SRCALPHA )
        title_with_alpha .set_alpha (current_alpha )
        title_with_alpha .blit (title_surface ,(0 ,0 ))
        window_surface .blit (title_with_alpha ,title_rect )


        score_text =f"Ваш итоговый счёт: {self.final_score}"
        score_color =(255 ,255 ,255 )
        score_surface =self .font .render (score_text ,True ,score_color )
        score_rect =score_surface .get_rect (center =(scaled_width //2 ,130 ))

        score_with_alpha =pygame .Surface (score_surface .get_size (),pygame .SRCALPHA )
        score_with_alpha .set_alpha (current_alpha )
        score_with_alpha .blit (score_surface ,(0 ,0 ))
        window_surface .blit (score_with_alpha ,score_rect )


        surface .blit (window_surface ,(scaled_x ,scaled_y ))


        for button in self .buttons :
            button .draw (surface )

class ConfirmExitWindow :
    """Окно подтверждения выхода из игры"""
    def __init__ (self ,screen_width ,screen_height ,button_class ,button_width ,button_height ,button_spacing ,font ):
        self .screen_width =screen_width 
        self .screen_height =screen_height 
        self .Button =button_class 
        self .button_width =button_width 
        self .button_height =button_height 
        self .button_spacing =button_spacing 
        self .font =font 


        self .window_width =500 
        self .window_height =300 
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


        button_center_x =self .window_x +(self .window_width -button_width )//2 
        button_y =self .window_y +220 

        self .exit_button =self .Button (button_center_x ,button_y ,button_width ,button_height ,"Выход",self .font )
        self .close_button_hovered =False 

    def show (self ):
        """Показывает окно с анимацией"""
        self .is_visible =True 
        self .animation_progress =0.0 

    def hide (self ):
        """Скрывает окно"""
        self .is_visible =False 
        self .animation_progress =0.0 

    def update (self ,dt ,mouse_pos ):
        """Обновляет состояние окна и анимацию"""
        if not self .is_visible :
            return None 


        if self .animation_progress <1.0 :
            self .animation_progress =min (1.0 ,self .animation_progress +self .animation_speed *dt )


        self .exit_button .check_hover (mouse_pos )
        self .exit_button .update_animation (dt )


        if self .animation_progress >=0.5 :
            close_rect =pygame .Rect (self .close_button_x ,self .close_button_y ,self .close_button_size ,self .close_button_size )
            self .close_button_hovered =close_rect .collidepoint (mouse_pos )
        else :
            self .close_button_hovered =False 

        return None 

    def handle_click (self ,mouse_pos ):
        """Обрабатывает клики по окну
        Возвращает "continue" для закрытия окна (крестик), "exit" для выхода в меню (кнопка "Выход")
        """
        if not self .is_visible or self .animation_progress <0.5 :
            return None 


        close_rect =pygame .Rect (self .close_button_x ,self .close_button_y ,self .close_button_size ,self .close_button_size )
        if close_rect .collidepoint (mouse_pos ):
            self .hide ()
            return "continue"


        if self .exit_button .is_clicked (mouse_pos ):
            self .hide ()
            return "exit"

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


        title_text ="Закончить охоту?"
        title_color =(182 ,233 ,17 )
        title_surface =self .font .render (title_text ,True ,title_color )
        title_rect =title_surface .get_rect (center =(scaled_width //2 ,60 ))
        title_with_alpha =pygame .Surface (title_surface .get_size (),pygame .SRCALPHA )
        title_with_alpha .set_alpha (current_alpha )
        title_with_alpha .blit (title_surface ,(0 ,0 ))
        window_surface .blit (title_with_alpha ,title_rect )


        warning_text ="Результат не будет сохранен."
        small_font =pygame .font .Font (None ,32 )
        warning_surface =small_font .render (warning_text ,True ,(255 ,255 ,255 ))
        warning_rect =warning_surface .get_rect (center =(scaled_width //2 ,130 ))
        warning_with_alpha =pygame .Surface (warning_surface .get_size (),pygame .SRCALPHA )
        warning_with_alpha .set_alpha (current_alpha )
        warning_with_alpha .blit (warning_surface ,(0 ,0 ))
        window_surface .blit (warning_with_alpha ,warning_rect )


        surface .blit (window_surface ,(scaled_x ,scaled_y ))


        self .exit_button .draw (surface )


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

def game_screen (screen ,clock ,fps ,Button ,BUTTON_WIDTH ,BUTTON_HEIGHT ,BUTTON_SPACING ,SCREEN_WIDTH ,SCREEN_HEIGHT ,font ,cap ,difficulty ="medium",settings_menu =None ):
    """Экран игры с механикой угадывания песен
    difficulty - уровень сложности: "easy", "medium", "hard"
    """

    all_songs =load_songs_from_folder (difficulty )

    if not all_songs :
        print (f"Ошибка: не найдено песен в папке для сложности {difficulty}")
        return "main_menu"


    if len (all_songs )<2 :
        print (f"Ошибка: недостаточно песен в папке для сложности {difficulty} (нужно минимум 2)")
        return "main_menu"


    songs_list =build_songs_list (all_songs )


    current_song_index =0 


    total_songs_in_level =len (songs_list )


    current_user =get_current_user ()


    current_score =0 


    feedback_state =None 
    feedback_pause_start =None 
    feedback_selected_index =None 
    FEEDBACK_PAUSE_DURATION =1.5 


    BUTTON_COLOR =(20 ,20 ,20 )
    BUTTON_HOVER_COLOR =(182 ,233 ,26 )
    BUTTON_WRONG_COLOR =(200 ,50 ,50 )


    background_path ="resources/menu/BackStatic.png"
    try :
        background_image =pygame .image .load (background_path )
        background_image =pygame .transform .scale (background_image ,(SCREEN_WIDTH ,SCREEN_HEIGHT ))
        background_loaded =True 
    except Exception as e :
        print (f"Предупреждение: не удалось загрузить фоновое изображение: {e}")
        background_loaded =False 
        background_image =None 


    try :
        sfx_correct =pygame .mixer .Sound ("resources/menu/correct.ogg")
    except Exception as e :
        print (f"Предупреждение: не удалось загрузить correct.ogg: {e}")
        sfx_correct =None 
    try :
        sfx_wrong =pygame .mixer .Sound ("resources/menu/wrong.ogg")
    except Exception as e :
        print (f"Предупреждение: не удалось загрузить wrong.ogg: {e}")
        sfx_wrong =None 



    COUNTER_H =36 
    SCORE_H =28 
    BAR_H =30 
    ANSWERS_H =BUTTON_HEIGHT *2 +30 

    GAP_COUNTER_SCORE =8 
    GAP_SCORE_BAR =20 
    GAP_BAR_ANSWERS =36 

    BLOCK_H =(COUNTER_H +GAP_COUNTER_SCORE +
    SCORE_H +GAP_SCORE_BAR +
    BAR_H +GAP_BAR_ANSWERS +
    ANSWERS_H )

    BLOCK_TOP =SCREEN_HEIGHT //2 -BLOCK_H //2 -120 


    COUNTER_Y =BLOCK_TOP 
    SCORE_Y =COUNTER_Y +COUNTER_H +GAP_COUNTER_SCORE 
    BAR_Y =SCORE_Y +SCORE_H +GAP_SCORE_BAR 
    ANSWERS_Y =BAR_Y +BAR_H +GAP_BAR_ANSWERS 


    BAR_W =800 
    BAR_X =SCREEN_WIDTH //2 -BAR_W //2 


    progress_bar =ProgressBar (
    x =BAR_X ,
    y =BAR_Y ,
    width =BAR_W ,
    height =BAR_H ,
    duration =20.0 
    )


    def start_new_round ():
        nonlocal current_song_index 


        if current_song_index >=len (songs_list ):
            current_song_index =0 


        current_song_path ,current_song_name ,answer_options ,correct_answer_index =generate_round (songs_list ,current_song_index )


        try :
            if pygame .mixer .music .get_busy ():
                pygame .mixer .music .stop ()
                pygame .time .wait (100 )

            pygame .mixer .music .load (current_song_path )
            pygame .mixer .music .play (0 )

            progress_bar .reset ()
            progress_bar .start ()
        except pygame .error as e :
            print (f"Ошибка при загрузке песни {current_song_path}: {e}")
            print (f"Рекомендация: конвертируйте файл в формат OGG для лучшей совместимости с pygame")
            try :
                pygame .mixer .music .stop ()
                progress_bar .reset ()
            except :
                pass 
        except Exception as e :
            print (f"Неожиданная ошибка при загрузке песни {current_song_path}: {e}")
            try :
                pygame .mixer .music .stop ()
                progress_bar .reset ()
            except :
                pass 

        return current_song_path ,current_song_name ,answer_options ,correct_answer_index 


    game_over_window =GameOverWindow (SCREEN_WIDTH ,SCREEN_HEIGHT ,Button ,BUTTON_WIDTH ,BUTTON_HEIGHT ,BUTTON_SPACING ,font )


    confirm_exit_window =ConfirmExitWindow (SCREEN_WIDTH ,SCREEN_HEIGHT ,Button ,BUTTON_WIDTH ,BUTTON_HEIGHT ,BUTTON_SPACING ,font )


    current_song_path ,current_song_name ,answer_options ,correct_answer_index =start_new_round ()


    ICON_BTN_SIZE =36 
    ICON_BTN_X =BAR_X +BAR_W +12 
    ICON_BTN_Y =BAR_Y +(BAR_H -ICON_BTN_SIZE )//2 
    icon_btn_rect =pygame .Rect (ICON_BTN_X ,ICON_BTN_Y ,ICON_BTN_SIZE ,ICON_BTN_SIZE )
    icon_btn_hovered =False 


    try :
        pause_icon =pygame .image .load ("resources/menu/pause.png")
        pause_icon =pygame .transform .scale (pause_icon ,(ICON_BTN_SIZE ,ICON_BTN_SIZE ))
    except Exception as e :
        print (f"Не удалось загрузить pause.png: {e}")
        pause_icon =None 

    try :
        play_icon =pygame .image .load ("resources/menu/play.png")
        play_icon =pygame .transform .scale (play_icon ,(ICON_BTN_SIZE ,ICON_BTN_SIZE ))
    except Exception as e :
        print (f"Не удалось загрузить play.png: {e}")
        play_icon =None 


    ANSWER_BUTTON_WIDTH =min (600 ,SCREEN_WIDTH -100 )
    button_start_y =ANSWERS_Y 
    button_spacing_x =ANSWER_BUTTON_WIDTH +50 
    button_spacing_y =BUTTON_HEIGHT +30 
    button_start_x_left =SCREEN_WIDTH //2 -button_spacing_x //2 -ANSWER_BUTTON_WIDTH //2 
    button_start_x_right =SCREEN_WIDTH //2 +button_spacing_x //2 -ANSWER_BUTTON_WIDTH //2 

    answer_buttons =[]
    for i in range (4 ):
        row =i //2 
        col =i %2 
        x =button_start_x_left if col ==0 else button_start_x_right 
        y =button_start_y +row *button_spacing_y 


        button_text =answer_options [i ]

        button =Button (x ,y ,ANSWER_BUTTON_WIDTH ,BUTTON_HEIGHT ,button_text ,font )
        answer_buttons .append (button )


    back_button =Button (
    SCREEN_WIDTH //2 -BUTTON_WIDTH //2 ,
    SCREEN_HEIGHT -BUTTON_HEIGHT -50 ,
    BUTTON_WIDTH ,
    BUTTON_HEIGHT ,
    "Назад",
    font 
    )



    if settings_menu is None :
        settings_menu =SettingsMenu (SCREEN_WIDTH ,SCREEN_HEIGHT ,
        vol_master =pygame .mixer .music .get_volume (),
        vol_music =1.0 ,vol_sfx =1.0 )


    def draw_game_frame (mouse_pos ,dt ):
        nonlocal feedback_state ,feedback_pause_start ,feedback_selected_index ,current_score 

        if not game_over_window .is_visible :
            ret ,frame =cap .read ()
            if not ret :
                cap .set (cv2 .CAP_PROP_POS_FRAMES ,0 )
        else :

            ret =False 


        if game_over_window .is_visible :
            game_over_window .update (dt ,mouse_pos )


        if confirm_exit_window .is_visible :
            confirm_exit_window .update (dt ,mouse_pos )


        if feedback_state is None and not game_over_window .is_visible and not confirm_exit_window .is_visible :
            for button in answer_buttons :
                button .check_hover (mouse_pos )
                button .update_animation (dt )
        else :


            for i ,button in enumerate (answer_buttons ):
                button .is_hovered =False 
                if feedback_state =="correct":

                    if i ==feedback_selected_index :
                        button .current_bg_color =BUTTON_HOVER_COLOR 
                        button .current_text_color =(0 ,0 ,0 )
                    else :
                        button .current_bg_color =BUTTON_COLOR 
                        button .current_text_color =(182 ,233 ,17 )
                elif feedback_state =="incorrect":

                    if i ==feedback_selected_index :
                        button .current_bg_color =BUTTON_WRONG_COLOR 
                        button .current_text_color =(255 ,255 ,255 )
                    elif i ==correct_answer_index :
                        button .current_bg_color =BUTTON_HOVER_COLOR 
                        button .current_text_color =(0 ,0 ,0 )
                    else :
                        button .current_bg_color =BUTTON_COLOR 
                        button .current_text_color =(182 ,233 ,17 )
                elif feedback_state =="timeout":

                    if i ==correct_answer_index :
                        button .current_bg_color =BUTTON_HOVER_COLOR 
                        button .current_text_color =(0 ,0 ,0 )
                    else :
                        button .current_bg_color =BUTTON_COLOR 
                        button .current_text_color =(182 ,233 ,17 )


        nonlocal icon_btn_hovered 
        if not confirm_exit_window .is_visible :
            icon_btn_hovered =icon_btn_rect .collidepoint (mouse_pos )


            back_button .check_hover (mouse_pos )
            back_button .update_animation (dt )


        progress_bar .update (dt )


        if progress_bar .is_complete ()and pygame .mixer .music .get_busy ():
            pygame .mixer .music .stop ()


        if (difficulty =="hard"
        and progress_bar .is_complete ()
        and feedback_state is None 
        and not game_over_window .is_visible 
        and not confirm_exit_window .is_visible ):
            current_score =apply_answer (current_score ,False ,current_user is not None )
            feedback_state ="timeout"
            feedback_selected_index =None 
            feedback_pause_start =pygame .time .get_ticks ()/1000.0 
            if sfx_wrong :
                sfx_wrong .play ()


        if background_loaded and background_image :
            screen .blit (background_image ,(0 ,0 ))
        else :
            screen .fill ((0 ,0 ,0 ))


        if not game_over_window .is_visible :

            song_counter_text =f"Песня {current_song_index + 1} из {total_songs_in_level}"
            counter_surface =font .render (song_counter_text ,True ,(182 ,233 ,17 ))
            counter_x =SCREEN_WIDTH //2 -counter_surface .get_width ()//2 
            screen .blit (counter_surface ,(counter_x ,COUNTER_Y ))


            if current_user :
                score_surface =font .render (f"Очки: {current_score}",True ,(182 ,233 ,17 ))
                screen .blit (score_surface ,
                (SCREEN_WIDTH //2 -score_surface .get_width ()//2 ,SCORE_Y ))
            else :
                small_font =pygame .font .Font (None ,28 )
                msg_surf =small_font .render (
                "Войдите в аккаунт, чтобы сохранить результат охоты.",
                True ,(150 ,150 ,150 ))
                screen .blit (msg_surf ,
                (SCREEN_WIDTH //2 -msg_surf .get_width ()//2 ,SCORE_Y ))


            elapsed =min (progress_bar .elapsed_time ,progress_bar .duration )
            remaining =progress_bar .duration -elapsed 
            timer_secs =int (remaining )if not progress_bar .is_complete ()else 0 
            timer_font =pygame .font .Font (None ,38 )
            timer_surf =timer_font .render (str (timer_secs ),True ,(182 ,233 ,17 ))
            timer_x =BAR_X -timer_surf .get_width ()-10 
            timer_y =BAR_Y +(BAR_H -timer_surf .get_height ())//2 
            screen .blit (timer_surf ,(timer_x ,timer_y ))


            progress_bar .draw (screen )



            if progress_bar .is_running :
                current_icon =pause_icon 
            else :
                current_icon =play_icon 


            btn_bg_color =(182 ,233 ,17 ,60 )if icon_btn_hovered else (30 ,30 ,30 ,160 )
            border_c_icon =(182 ,233 ,17 )if icon_btn_hovered else (80 ,80 ,80 )
            btn_surf =pygame .Surface ((ICON_BTN_SIZE ,ICON_BTN_SIZE ),pygame .SRCALPHA )
            pygame .draw .rect (btn_surf ,btn_bg_color ,(0 ,0 ,ICON_BTN_SIZE ,ICON_BTN_SIZE ),border_radius =6 )
            pygame .draw .rect (btn_surf ,border_c_icon ,(0 ,0 ,ICON_BTN_SIZE ,ICON_BTN_SIZE ),2 ,border_radius =6 )
            screen .blit (btn_surf ,(ICON_BTN_X ,ICON_BTN_Y ))
            if current_icon :
                screen .blit (current_icon ,(ICON_BTN_X ,ICON_BTN_Y ))
            else :
                fallback_font =pygame .font .Font (None ,24 )
                fb_text ="||"if progress_bar .is_running else ">"
                fb_surf =fallback_font .render (fb_text ,True ,(182 ,233 ,17 ))
                screen .blit (fb_surf ,(ICON_BTN_X +(ICON_BTN_SIZE -fb_surf .get_width ())//2 ,
                ICON_BTN_Y +(ICON_BTN_SIZE -fb_surf .get_height ())//2 ))


            for button in answer_buttons :
                button .draw (screen )


            back_button .draw (screen )


        if game_over_window .is_visible :
            game_over_window .draw (screen )


        if confirm_exit_window .is_visible :
            confirm_exit_window .draw (screen )


        settings_menu .update (dt )
        settings_menu .draw (screen ,mouse_pos )


        sfx_volume =settings_menu .vol_master *settings_menu .vol_sfx 
        if sfx_correct :
            sfx_correct .set_volume (sfx_volume )
        if sfx_wrong :
            sfx_wrong .set_volume (sfx_volume )


    def draw_game ():
        draw_game_frame (pygame .mouse .get_pos (),0.016 )

    if not fade_in (screen ,clock ,fps ,draw_game ,SCREEN_WIDTH ,SCREEN_HEIGHT ,duration =0.3 ):
        return "quit"

    running =True 

    while running :
        dt =clock .tick (fps )/1000.0 
        dt =min (dt ,0.1 )

        mouse_pos =pygame .mouse .get_pos ()

        for event in pygame .event .get ():
            if event .type ==pygame .QUIT :
                return "quit"


            if settings_menu .handle_event (event ,mouse_pos ):
                continue 

            elif event .type ==pygame .KEYDOWN :
                if event .key ==pygame .K_ESCAPE :

                    if not game_over_window .is_visible :
                        confirm_exit_window .show ()
                elif event .key ==pygame .K_SPACE :

                    if progress_bar .is_running :
                        progress_bar .stop ()
                        pygame .mixer .music .pause ()
                    elif progress_bar .is_complete ():

                        try :
                            pygame .mixer .music .load (current_song_path )
                            pygame .mixer .music .play (0 )
                            progress_bar .reset ()
                            progress_bar .start ()
                        except Exception as e :
                            print (f"Ошибка при перезапуске музыки: {e}")
                    else :
                        progress_bar .start ()
                        pygame .mixer .music .unpause ()
            elif event .type ==pygame .MOUSEBUTTONDOWN :
                if event .button ==1 :

                    if confirm_exit_window .is_visible :
                        action =confirm_exit_window .handle_click (mouse_pos )
                        if action =="continue":

                            confirm_exit_window .hide ()
                        elif action =="exit":

                            confirm_exit_window .hide ()

                            pygame .mixer .music .stop ()
                            progress_bar .stop ()

                            if fade_out (screen ,clock ,fps ,draw_game ,SCREEN_WIDTH ,SCREEN_HEIGHT ,duration =0.3 ):
                                return "main_menu"
                    elif back_button .is_clicked (mouse_pos ):

                        confirm_exit_window .show ()
                    elif icon_btn_rect .collidepoint (mouse_pos ):

                        if progress_bar .is_running :
                            progress_bar .stop ()
                            pygame .mixer .music .pause ()
                        elif progress_bar .is_complete ():
                            try :
                                pygame .mixer .music .load (current_song_path )
                                pygame .mixer .music .play (0 )
                                progress_bar .reset ()
                                progress_bar .start ()
                            except Exception as e :
                                print (f"Ошибка при перезапуске музыки: {e}")
                        else :
                            progress_bar .start ()
                            pygame .mixer .music .unpause ()

                    elif game_over_window .is_visible :
                        action =game_over_window .handle_click (mouse_pos )
                        if action =="exit":


                            pygame .mixer .music .stop ()
                            progress_bar .stop ()


                            if fade_out (screen ,clock ,fps ,draw_game ,SCREEN_WIDTH ,SCREEN_HEIGHT ,duration =0.3 ):
                                return "main_menu"
                        elif action =="restart":


                            pygame .mixer .music .stop ()
                            progress_bar .stop ()


                            return f"restart_{difficulty}"




                    if feedback_state is None and not game_over_window .is_visible and not confirm_exit_window .is_visible :
                            for i ,button in enumerate (answer_buttons ):
                                if button .is_clicked (mouse_pos ):

                                    pygame .mixer .music .stop ()
                                    progress_bar .stop ()

                                    if i ==correct_answer_index :

                                        current_score =apply_answer (current_score ,True ,current_user is not None )
                                        feedback_state ="correct"
                                        feedback_selected_index =i 
                                        feedback_pause_start =pygame .time .get_ticks ()/1000.0 
                                        if sfx_correct :
                                            sfx_correct .play ()
                                    else :

                                        current_score =apply_answer (current_score ,False ,current_user is not None )
                                        feedback_state ="incorrect"
                                        feedback_selected_index =i 
                                        feedback_pause_start =pygame .time .get_ticks ()/1000.0 
                                        if sfx_wrong :
                                            sfx_wrong .play ()

                                    break 




        if feedback_state is not None and feedback_pause_start is not None :
            current_time =pygame .time .get_ticks ()/1000.0 
            elapsed_time =current_time -feedback_pause_start 


            pause_duration =2.0 if feedback_state =="timeout"else FEEDBACK_PAUSE_DURATION 

            if elapsed_time >=pause_duration :


                for button in answer_buttons :
                    button .current_bg_color =BUTTON_COLOR 
                    button .current_text_color =(182 ,233 ,17 )
                    button .animation_progress =0.0 


                feedback_state =None 
                feedback_pause_start =None 
                feedback_selected_index =None 


                current_song_index +=1 


                if current_song_index >=total_songs_in_level :


                    if current_user :
                        user_name =current_user [0 ]
                        update_best_score (user_name ,difficulty ,current_score )


                    pygame .mixer .music .stop ()
                    progress_bar .stop ()


                    game_over_window .show (current_score )
                else :

                    current_song_path ,current_song_name ,answer_options ,correct_answer_index =start_new_round ()


                    for j ,btn in enumerate (answer_buttons ):

                        button_text =answer_options [j ]
                        btn .text =button_text 


        if confirm_exit_window .is_visible :


            pass 


        draw_game_frame (mouse_pos ,dt )
        pygame .display .flip ()


    pygame .mixer .music .stop ()
    progress_bar .stop ()
    return "main_menu"

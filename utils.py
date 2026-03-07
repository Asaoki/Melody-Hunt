import pygame 


BUTTON_WIDTH =380 
BUTTON_HEIGHT =62 
BUTTON_SPACING =16 
BUTTON_SKEW =28 
BUTTON_COLOR =(12 ,12 ,16 )
BUTTON_HOVER_COLOR =(182 ,233 ,26 )
BUTTON_TEXT_COLOR =(182 ,233 ,17 )
BUTTON_TEXT_HOVER_COLOR =(0 ,0 ,0 )
BUTTON_BORDER_COLOR =(182 ,233 ,17 )
BUTTON_BORDER_WIDTH =2 
BUTTON_ALPHA =210 
BUTTON_ANIMATION_SPEED =10.0 


def lerp_color (color1 ,color2 ,t ):
    """Линейная интерполяция между двумя цветами"""
    t =max (0 ,min (1 ,t ))
    return tuple (int (color1 [i ]+(color2 [i ]-color1 [i ])*t )for i in range (3 ))


class Button :
    def __init__ (self ,x ,y ,width ,height ,text ,font =None ):
        self .x =x 
        self .y =y 
        self .width =width 
        self .height =height 
        self .text =text 
        self .font =font 
        self .is_hovered =False 

        self .current_bg_color =BUTTON_COLOR 
        self .current_text_color =BUTTON_TEXT_COLOR 

        self .animation_progress =0.0 


        self .rect =pygame .Rect (x -BUTTON_SKEW //2 ,y ,width +BUTTON_SKEW ,height )

    def update_animation (self ,dt ):
        """Обновляет анимацию изменения цветов
        dt - время, прошедшее с последнего кадра в секундах
        """
        target_progress =1.0 if self .is_hovered else 0.0 


        progress_change =BUTTON_ANIMATION_SPEED *dt 


        if self .animation_progress <target_progress :
            self .animation_progress =min (1.0 ,self .animation_progress +progress_change )
        elif self .animation_progress >target_progress :
            self .animation_progress =max (0.0 ,self .animation_progress -progress_change )


        self .current_bg_color =lerp_color (BUTTON_COLOR ,BUTTON_HOVER_COLOR ,self .animation_progress )


        self .current_text_color =lerp_color (BUTTON_TEXT_COLOR ,BUTTON_TEXT_HOVER_COLOR ,self .animation_progress )

    def get_parallelogram_points (self ):
        """Возвращает координаты вершин параллелограмма"""
        skew_half =BUTTON_SKEW //2 

        top_left =(self .x +skew_half ,self .y )

        top_right =(self .x +self .width +skew_half ,self .y )

        bottom_right =(self .x +self .width -skew_half ,self .y +self .height )

        bottom_left =(self .x -skew_half ,self .y +self .height )

        return [top_left ,top_right ,bottom_right ,bottom_left ]

    def draw (self ,surface ):
        color =self .current_bg_color 
        points =self .get_parallelogram_points ()

        min_x =min (p [0 ]for p in points )
        min_y =min (p [1 ]for p in points )
        max_x =max (p [0 ]for p in points )
        max_y =max (p [1 ]for p in points )


        glow_pad =6 
        surf_w =max_x -min_x +glow_pad *2 
        surf_h =max_y -min_y +glow_pad *2 
        button_surface =pygame .Surface ((surf_w ,surf_h ),pygame .SRCALPHA )


        offset_points =[(p [0 ]-min_x +glow_pad ,p [1 ]-min_y +glow_pad )for p in points ]


        if self .animation_progress >0 :
            glow_alpha =int (60 *self .animation_progress )
            glow_color =(*BUTTON_HOVER_COLOR ,glow_alpha )
            for glow_width in (6 ,4 ,2 ):
                pygame .draw .polygon (button_surface ,glow_color ,offset_points ,glow_width +BUTTON_BORDER_WIDTH )


        pygame .draw .polygon (button_surface ,(*color ,BUTTON_ALPHA ),offset_points )


        border_alpha =255 if self .animation_progress >0.05 else 160 
        border_color =lerp_color (BUTTON_BORDER_COLOR ,BUTTON_HOVER_COLOR ,self .animation_progress )
        pygame .draw .polygon (button_surface ,(*border_color ,border_alpha ),offset_points ,BUTTON_BORDER_WIDTH )

        surface .blit (button_surface ,(min_x -glow_pad ,min_y -glow_pad ))


        if self .font :
            text_color =self .current_text_color 
            text_surface =self .font .render (self .text ,True ,text_color )
            center_x =self .x +self .width //2 
            center_y =self .y +self .height //2 
            text_rect =text_surface .get_rect (center =(center_x ,center_y ))
            surface .blit (text_surface ,text_rect )

    def check_hover (self ,pos ):

        points =self .get_parallelogram_points ()
        self .is_hovered =self ._point_in_polygon (pos ,points )
        return self .is_hovered 

    def _point_in_polygon (self ,point ,polygon ):
        """Проверяет, находится ли точка внутри многоугольника (алгоритм ray casting)"""
        x ,y =point 
        n =len (polygon )
        inside =False 

        p1x ,p1y =polygon [0 ]
        for i in range (1 ,n +1 ):
            p2x ,p2y =polygon [i %n ]
            if y >min (p1y ,p2y ):
                if y <=max (p1y ,p2y ):
                    if x <=max (p1x ,p2x ):
                        if p1y !=p2y :
                            xinters =(y -p1y )*(p2x -p1x )/(p2y -p1y )+p1x 
                        if p1x ==p2x or x <=xinters :
                            inside =not inside 
            p1x ,p1y =p2x ,p2y 

        return inside 

    def is_clicked (self ,pos ):
        return self .check_hover (pos )


def fade_out (screen ,clock ,fps ,draw_function ,SCREEN_WIDTH ,SCREEN_HEIGHT ,duration =0.3 ):
    """Плавное затемнение экрана до черного
    duration - длительность анимации в секундах
    draw_function - функция для отрисовки текущего экрана (вызывается каждый кадр)
    """
    fade_surface =pygame .Surface ((SCREEN_WIDTH ,SCREEN_HEIGHT ))
    fade_surface .fill ((0 ,0 ,0 ))

    alpha =0 
    alpha_increment =255 /(fps *duration )

    while alpha <255 :
        dt =clock .tick (fps )/1000.0 
        dt =min (dt ,0.1 )


        for event in pygame .event .get ():
            if event .type ==pygame .QUIT :
                return False 


        draw_function ()


        fade_surface .set_alpha (int (alpha ))
        screen .blit (fade_surface ,(0 ,0 ))

        pygame .display .flip ()

        alpha +=alpha_increment 
        if alpha >255 :
            alpha =255 


    draw_function ()
    fade_surface .set_alpha (255 )
    screen .blit (fade_surface ,(0 ,0 ))
    pygame .display .flip ()

    return True 


def fade_in (screen ,clock ,fps ,draw_function ,SCREEN_WIDTH ,SCREEN_HEIGHT ,duration =0.3 ):
    """Плавное осветление экрана от черного
    duration - длительность анимации в секундах
    draw_function - функция для отрисовки нового экрана (вызывается каждый кадр)
    """
    fade_surface =pygame .Surface ((SCREEN_WIDTH ,SCREEN_HEIGHT ))
    fade_surface .fill ((0 ,0 ,0 ))

    alpha =255 
    alpha_decrement =255 /(fps *duration )

    while alpha >0 :
        dt =clock .tick (fps )/1000.0 
        dt =min (dt ,0.1 )


        for event in pygame .event .get ():
            if event .type ==pygame .QUIT :
                return False 


        draw_function ()


        fade_surface .set_alpha (int (alpha ))
        screen .blit (fade_surface ,(0 ,0 ))

        pygame .display .flip ()

        alpha -=alpha_decrement 
        if alpha <0 :
            alpha =0 


    draw_function ()
    pygame .display .flip ()

    return True 

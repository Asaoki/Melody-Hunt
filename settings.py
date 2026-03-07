import pygame 

ACCENT =(182 ,233 ,17 )
BG_COLOR =(14 ,14 ,18 )
BORDER_COL =(182 ,233 ,17 )
GRAY =(110 ,110 ,115 )
WHITE =(220 ,220 ,220 )
DIM_COLOR =(50 ,50 ,55 )


class _Slider :
    """Горизонтальный слайдер громкости."""
    TRACK_H =6 
    THUMB_R =9 

    def __init__ (self ,rel_x ,rel_y ,width ,value =1.0 ):
        self .rx =rel_x 
        self .ry =rel_y 
        self .w =width 
        self .value =max (0.0 ,min (1.0 ,value ))
        self .dragging =False 
        self ._abs_x =0 
        self ._abs_y =0 

    def set_abs (self ,panel_x ,panel_y ):
        self ._abs_x =panel_x +self .rx 
        self ._abs_y =panel_y +self .ry 

    def _thumb_abs_x (self ):
        return int (self ._abs_x +self .w *self .value )

    def _hit_rect (self ):
        r =self .THUMB_R +6 
        return pygame .Rect (self ._thumb_abs_x ()-r ,
        self ._abs_y -r ,r *2 ,r *2 )

    def handle_down (self ,pos ):
        if self ._hit_rect ().collidepoint (pos ):
            self .dragging =True 
            return True 
        tx ,ty =pos 
        if (self ._abs_x <=tx <=self ._abs_x +self .w and 
        self ._abs_y -self .THUMB_R -8 <=ty <=self ._abs_y +self .THUMB_R +8 ):
            self .value =max (0.0 ,min (1.0 ,(tx -self ._abs_x )/self .w ))
            self .dragging =True 
            return True 
        return False 

    def handle_motion (self ,pos ):
        if self .dragging :
            self .value =max (0.0 ,min (1.0 ,(pos [0 ]-self ._abs_x )/self .w ))

    def handle_up (self ):
        self .dragging =False 

    def draw_on (self ,surf ,mouse_pos_abs ,alpha ,disabled =False ):
        a =min (255 ,max (0 ,alpha ))
        ox ,oy =self .rx ,self .ry 

        track_col =(40 ,40 ,44 )
        filled_col =(80 ,82 ,78 )if disabled else ACCENT 
        hovered =self ._hit_rect ().collidepoint (mouse_pos_abs )
        thumb_col =(80 ,82 ,78 )if disabled else (
        (220 ,255 ,80 )if (hovered or self .dragging )else ACCENT 
        )


        pygame .draw .rect (surf ,(*track_col ,a ),
        (ox ,oy -self .TRACK_H //2 ,self .w ,self .TRACK_H ),
        border_radius =3 )

        filled =int (self .w *self .value )
        if filled >0 :
            pygame .draw .rect (surf ,(*filled_col ,a ),
            (ox ,oy -self .TRACK_H //2 ,filled ,self .TRACK_H ),
            border_radius =3 )

        tx =ox +int (self .w *self .value )
        pygame .draw .circle (surf ,(*BG_COLOR ,a ),(tx ,oy ),self .THUMB_R )
        pygame .draw .circle (surf ,(*thumb_col ,a ),(tx ,oy ),self .THUMB_R ,3 )


        pct_font =pygame .font .Font (None ,24 )
        pct_text =f"{int(self.value * 100)}%"
        pct_col =(70 ,72 ,68 )if disabled else thumb_col 
        pct =pct_font .render (pct_text ,True ,pct_col )
        pct_s =pygame .Surface (pct .get_size (),pygame .SRCALPHA )
        pct_s .set_alpha (a )
        pct_s .blit (pct ,(0 ,0 ))
        surf .blit (pct_s ,(ox +self .w +12 ,oy -pct .get_height ()//2 ))


class SettingsMenu :
    PANEL_W =440 
    PADDING =26 

    def __init__ (self ,screen_width ,screen_height ,
    vol_master =1.0 ,vol_music =1.0 ,vol_sfx =1.0 ):

        self .sw =screen_width 
        self .sh =screen_height 

        self .slide =0.0 
        self .target =0.0 
        self .SPEED =9.0 
        self .visible =False 

        self .PANEL_H =318 
        self .panel_x =screen_width -self .PANEL_W -16 
        self .panel_y =70 

        P =self .PADDING 
        sw =self .PANEL_W -P *2 -56 


        self .sliders ={
        "master":_Slider (P ,122 ,sw ,vol_master ),
        "music":_Slider (P ,192 ,sw ,vol_music ),
        "sfx":_Slider (P ,262 ,sw ,vol_sfx ),
        }
        for sl in self .sliders .values ():
            sl .set_abs (self .panel_x ,self .panel_y )


        self .gear_size =38 
        self .gear_x =screen_width -self .gear_size -16 
        self .gear_y =16 
        self .gear_rect =pygame .Rect (self .gear_x ,self .gear_y ,
        self .gear_size ,self .gear_size )
        try :
            img =pygame .image .load (
            "resources/menu/settings-gear.png").convert_alpha ()
            self .gear_img =pygame .transform .scale (
            img ,(self .gear_size ,self .gear_size ))
        except Exception as e :
            print (f"settings-gear.png не загружена: {e}")
            self .gear_img =None 


    @property 
    def is_open (self ):
        return self .target >0.5 

    @property 
    def vol_master (self ):
        return self .sliders ["master"].value 

    @property 
    def vol_music (self ):
        return self .sliders ["music"].value 

    @property 
    def vol_sfx (self ):
        return self .sliders ["sfx"].value 

    def toggle (self ):
        self .target =0.0 if self .is_open else 1.0 
        if self .target >0.5 :
            self .visible =True 


    def update (self ,dt ):
        diff =self .target -self .slide 
        if abs (diff )>0.001 :
            self .slide =max (0.0 ,min (1.0 ,
            self .slide +diff *self .SPEED *dt ))
        else :
            self .slide =self .target 
        if self .slide <=0.001 :
            self .slide =0.0 
            self .visible =False 


        pygame .mixer .music .set_volume (self .vol_master *self .vol_music )


    def handle_event (self ,event ,mouse_pos ):
        """Возвращает True если событие поглощено."""


        if event .type ==pygame .MOUSEBUTTONDOWN and event .button ==1 :
            if self .gear_rect .collidepoint (mouse_pos ):
                self .toggle ()
                return True 

        if not self .visible or self .slide <0.05 :
            return False 

        panel_rect =pygame .Rect (self .panel_x ,self .panel_y ,
        self .PANEL_W ,self .PANEL_H )

        if event .type ==pygame .MOUSEBUTTONDOWN and event .button ==1 :
            if not panel_rect .collidepoint (mouse_pos ):
                self .target =0.0 
                return True 


            if self .sliders ["master"].handle_down (mouse_pos ):
                return True 
            if self .sliders ["music"].handle_down (mouse_pos ):
                return True 
            if self .sliders ["sfx"].handle_down (mouse_pos ):
                return True 
            return True 

        if event .type ==pygame .MOUSEMOTION :
            self .sliders ["master"].handle_motion (mouse_pos )
            self .sliders ["music"].handle_motion (mouse_pos )
            self .sliders ["sfx"].handle_motion (mouse_pos )
            return False 

        if event .type ==pygame .MOUSEBUTTONUP and event .button ==1 :
            self .sliders ["master"].handle_up ()
            self .sliders ["music"].handle_up ()
            self .sliders ["sfx"].handle_up ()
            return False 

        return False 


    def draw (self ,surface ,mouse_pos ):


        gear_hov =self .gear_rect .collidepoint (mouse_pos )
        if self .gear_img :
            img =self .gear_img .copy ()
            if gear_hov or self .is_open :
                tint =pygame .Surface (img .get_size (),pygame .SRCALPHA )
                tint .fill ((*ACCENT ,60 ))
                img .blit (tint ,(0 ,0 ),special_flags =pygame .BLEND_RGBA_ADD )
            surface .blit (img ,(self .gear_x ,self .gear_y ))
        else :
            fb_col =ACCENT if (gear_hov or self .is_open )else WHITE 
            fb =pygame .font .Font (None ,38 ).render ("[S]",True ,fb_col )
            surface .blit (fb ,(self .gear_x ,self .gear_y ))

        if not self .visible or self .slide <=0.0 :
            return 


        t =1 -(1 -self .slide )**3 
        alpha =int (255 *t )


        dim =pygame .Surface ((self .sw ,self .sh ),pygame .SRCALPHA )
        dim .fill ((0 ,0 ,0 ,int (85 *t )))
        surface .blit (dim ,(0 ,0 ))


        P =self .PADDING 
        panel_surf =pygame .Surface ((self .PANEL_W ,self .PANEL_H ),pygame .SRCALPHA )

        pygame .draw .rect (panel_surf ,(*BG_COLOR ,int (248 *t )),
        (0 ,0 ,self .PANEL_W ,self .PANEL_H ),border_radius =8 )
        pygame .draw .rect (panel_surf ,(*BORDER_COL ,alpha ),
        (0 ,0 ,self .PANEL_W ,self .PANEL_H ),2 ,border_radius =8 )

        f_title =pygame .font .Font (None ,42 )
        f_sec =pygame .font .Font (None ,28 )
        f_lbl =pygame .font .Font (None ,26 )

        def _blit (text ,x ,y ,color ,font ):
            s =font .render (text ,True ,color )
            ss =pygame .Surface (s .get_size (),pygame .SRCALPHA )
            ss .set_alpha (alpha )
            ss .blit (s ,(0 ,0 ))
            panel_surf .blit (ss ,(x ,y ))

        def _line (y ,col =DIM_COLOR ,a_mul =180 ):
            pygame .draw .line (panel_surf ,(*col ,int (a_mul *t )),
            (P ,y ),(self .PANEL_W -P ,y ),1 )


        _blit ("НАСТРОЙКИ",(self .PANEL_W -f_title .size ("НАСТРОЙКИ")[0 ])//2 ,
        14 ,ACCENT ,f_title )
        _line (48 ,ACCENT ,100 )


        _blit ("ЗВУК",P ,56 ,ACCENT ,f_sec )
        _line (80 )

        _blit ("Общая громкость",P ,96 ,GRAY ,f_lbl )


        _blit ("Музыка",P ,166 ,GRAY ,f_lbl )


        _blit ("Звуки",P ,236 ,GRAY ,f_lbl )


        _line (295 )


        self .sliders ["master"].draw_on (panel_surf ,mouse_pos ,alpha ,disabled =False )
        self .sliders ["music"].draw_on (panel_surf ,mouse_pos ,alpha ,disabled =False )
        self .sliders ["sfx"].draw_on (panel_surf ,mouse_pos ,alpha ,disabled =False )

        surface .blit (panel_surf ,(self .panel_x ,self .panel_y ))

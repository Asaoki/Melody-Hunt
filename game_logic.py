import os 
import random 


MAX_SONGS_PER_LEVEL =20 


SCORE_CORRECT =50 
SCORE_WRONG =-50 


def load_songs_from_folder (difficulty ):
    """Загружает список всех песен из папки выбранной сложности.
    Возвращает список кортежей (полный_путь, название_без_расширения)
    """
    folder_path =f"resources/gamemodes/{difficulty}"

    if not os .path .exists (folder_path ):
        print (f"Предупреждение: папка {folder_path} не найдена")
        return []

    songs =[]
    for filename in os .listdir (folder_path ):
        if filename .lower ().endswith (('.mp3','.wav','.ogg','.flac','.m4a')):
            full_path =os .path .join (folder_path ,filename )
            song_name =os .path .splitext (filename )[0 ]
            songs .append ((full_path ,song_name ))

    return songs 


def build_songs_list (all_songs ):
    """Из полного списка песен выбирает и перемешивает до MAX_SONGS_PER_LEVEL треков.
    Возвращает итоговый список песен для сессии.
    """
    if len (all_songs )>MAX_SONGS_PER_LEVEL :
        songs_list =random .sample (all_songs ,MAX_SONGS_PER_LEVEL )
    else :
        songs_list =all_songs .copy ()

    random .shuffle (songs_list )
    return songs_list 


def generate_round (songs_list ,current_song_index ):
    """Генерирует данные для одного раунда.
    Возвращает (song_path, song_name, answer_options, correct_answer_index)
    """
    current_song_path ,current_song_name =songs_list [current_song_index ]


    wrong_answers =[name for _ ,name in songs_list if name !=current_song_name ]


    if len (wrong_answers )<3 :
        extended_wrong =wrong_answers .copy ()
        while len (extended_wrong )<3 :
            extended_wrong .extend (wrong_answers )
        wrong_answers =extended_wrong 

    selected_wrong =random .sample (wrong_answers ,3 )

    answer_options =[current_song_name ]+selected_wrong 
    random .shuffle (answer_options )

    correct_answer_index =answer_options .index (current_song_name )

    return current_song_path ,current_song_name ,answer_options ,correct_answer_index 


def apply_answer (current_score ,is_correct ,user_authorized ):
    """Применяет результат ответа к счёту.
    Возвращает новый счёт.
    """
    if not user_authorized :
        return current_score 

    if is_correct :
        return current_score +SCORE_CORRECT 
    else :
        return current_score +SCORE_WRONG 

import cv2
import os
import glob
from animateplot.video.exceptions_animateplot import DirectoryNotExists



class RenderVideo:
    __dir_pattern_imgs = '.data'
    
    
    def __init__(self,list_images:list,fps:int=8.7) -> None:
        self.__images = list_images
        self.__fps = fps# [file for file in glob.glob(self.__dir_pattern_imgs+'/*.png')]
        self.__images.sort(key=os.path.getmtime)
        # if os.path.isdir(dir):
        #     self.__dir_pattern_imgs = dir
        #     self.__fps = fps
        #     self.__images = [file for file in glob.glob(self.__dir_pattern_imgs+'/*.png')]
        #     self.__images.sort(key=os.path.getmtime)
        # else:
        #     raise DirectoryNotExists(f'the pathDir {dir} not exist or not is a directory',dir)
    
    
    def render_mp4(self,path_video:str):
        first_img = cv2.imread(self.__images[0])#os.path.join(self.__dir_pattern_imgs,self.__images[0]))
        y,x,_ = first_img.shape
        
        video = cv2.VideoWriter(path_video,cv2.VideoWriter_fourcc('m','p','4','v'),self.__fps,(x,y))
        for img in self.__images:
            dir_img = os.path.join(self.__dir_pattern_imgs,img)
            image = cv2.imread(img)
            video.write(image)
        
        video.release()
        cv2.destroyAllWindows()






# # Definir o caminho para a pasta de fotos
# diretorio = 'caminho/para/sua/pasta/de/fotos'

# # Definir a taxa de quadros do vídeo
# fps = 30

# # Obter a lista de nomes de arquivo PNG na pasta
# arquivos_png = [arquivo for arquivo in os.listdir(diretorio) if arquivo.endswith('.png')]

# # Classificar a lista em ordem alfabética
# arquivos_png.sort()

# # Obter o primeiro arquivo PNG para obter a largura e altura da imagem
# primeiro_arquivo = cv2.imread(os.path.join(diretorio, arquivos_png[0]))
# altura, largura, _ = primeiro_arquivo.shape

# # Criar um objeto VideoWriter para escrever o vídeo
# video = cv2.VideoWriter('video.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (largura, altura))

# # Loop pelos arquivos PNG e adicionar cada quadro ao vídeo
# for arquivo in arquivos_png:
#     caminho_completo = os.path.join(diretorio, arquivo)
#     imagem = cv2.imread(caminho_completo)
#     video.write(imagem)

# # Liberar o objeto VideoWriter e fechar o vídeo
# video.release()
# cv2.destroyAllWindows()
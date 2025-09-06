import matplotlib.pyplot as plt
import imageio
import os, glob
import time

from animateplot.video.video_movie import RenderVideo as rv
from ipywidgets import Video
#from tqdm import tqdmgit 
from statistics import mode,median
import numpy as np
ping_list = [0]
time_list = [time.time()]
ping_last = 0


class AnimatePlot:
  pattern_savefig = '%(i)s_fig.png'
  pattern_dir = '.data'
  images = None
  
  def __init__(self,x=None,callplot:plt=None,plt:plt=plt,args=None,dpi=None):
    self.__pattern_dir_check()
    self.args = args
    if((type(x)==list or type(x)==np.ndarray) and callplot and plt):
        self.plot = callplot
        self.x = x
        self.size = len(self.x)
    self.plt = plt
    self.dpi = dpi



  def render_cache(self):
    time_list = [time.time()]
    ping_list = [0]
    self.images = []
    if not os.path.isdir(self.pattern_dir):
      self.images = [file for file in glob.glob(self.pattern_dir+'/'+'*.png')]
      self.images.sort(key=os.path.getmtime)
#      print(f'find {len(self.images)} images in cache! \ngetting it images...')
    
    else:
      time_init = time_list[0]

      for i,x in (enumerate(self.x)):
        self.__pattern_dir_check()
        #print(f'[rendering: {i}/{self.size} images from {self.f.__name__}]',flush=True,end='\r')
        #f = self.f(self.x[:i],*self.args)[:i] if self.args else self.f(self.x[:i])[:i]
        plot = self.plot(i,self.plt)
        img_plot = self.pattern_dir+'/'+self.pattern_savefig%{'i':str(i)}
        if self.dpi:
          plot.savefig(img_plot,dpi=self.dpi)
        else:
          plot.savefig(img_plot)
        plot.cla()
        plot.clf()
        self.images.append(img_plot)
        
        ping = time.time() - time_list[-1]
        ping_list.append(ping)
        time_list.append(time.time())
        ping_med = median(ping_list) #sum(ping_list)/len(ping_list)
        time_last = time.time() - time_init #ping_list[0]
        rest_time = ping_med*(self.size-i)
        total_time = rest_time+time_last
        print(f'rendering plots {i}/{self.size} [{(100*i/self.size):.2f}% |  {(ping_med):.2f} f/s  |  {time_last:.1f}s | {rest_time:.1f}s | {total_time:.1f}s ]',end='\r',flush=True)

      ping_total = time.time()-time_init
      ping = 1000*ping_total/self.size
      speed = self.size/ping_total
      print(f'ended saved cache images! \n[{self.size} images saved in {ping_total:.1f}s | speed: {speed:.1f}/img/s | ping: {ping:.1f}ms]')
      ping_med = 0
      time_last = 0
      rest_time = 0
      total_time = 0
    



  def render_gif(self,path,fps=8.9):
    time_init = time.time()
    imgs_imread = []

    if len(self.images)>10:
      for i,img in enumerate(self.images):
        imgs_imread.append(imageio.imread(img))
      imageio.mimsave(path,imgs_imread,fps=fps)
      ping_total = time.time() - time_init
    
    else:
      file_imgs = [file for file in glob.glob(self.pattern_dir+'/*.png')]

      if file_imgs:
        imgs_imread = []
        for i,img in enumerate(file_imgs):
          imgs_imread.append(imageio.imread(img))
        imageio.mimsave(path,imgs_imread,fps=fps)
    ping_total = time.time() - time_init
    print(f'{path} saved in {ping_total:.1f}s')

  

  def render_mp4(self,path_video,fps=8.7,duration=None):
    render_video = rv(self.images,fps=fps)
    render_video.render_mp4(path_video)
    return self.play_jb_mp4(path_video)
  
  
  def play_jb_mp4(self,path):
    if 'JPY_PARENT_PID' in os.environ:
     
      if os.path.isfile(path):
        print(f"playing {path}")
        return Video.from_file(path, width=600, height=350)
      else:
        return 0
    else:
      return 0
 
 
  
  



  def __pattern_dir_check(self):
    if not os.path.isdir(self.pattern_dir):
      os.mkdir(self.pattern_dir)

  def delete_cache(self):
    if os.path.isdir(self.pattern_dir):
      file_imgs = [file for file in glob.glob(self.pattern_dir+'/*.png')]
      for i,image in enumerate(file_imgs):
        os.remove(image)
      os.rmdir(self.pattern_dir)






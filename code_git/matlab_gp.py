import matlab.engine
eng = matlab.engine.start_matlab()
eng.addpath(r'C:\Users\Equipo\Desktop\gpml', nargout=0)
eng.startup(nargout=0)
eng.ejemplo_gp(nargout=0)

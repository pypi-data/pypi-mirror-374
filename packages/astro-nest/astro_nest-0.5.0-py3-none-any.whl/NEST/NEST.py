import numpy as np
import pickle,json,os,warnings
try:
    from tqdm import tqdm
    has_tqdm = True
except ImportError:
    has_tqdm = False
NNSA_DIR = os.path.dirname(os.path.abspath(__file__))

def custom_warning(message, category, filename, lineno, file=None, line=None):
    print(f"{category.__name__}: {message}")

warnings.showwarning = custom_warning

def get_mode(arr,min_age=0,max_age=14):
    hist, bins = np.histogram(arr,bins=100,range=(min_age,max_age))
    return bins[np.argmax(hist)] + (bins[1]-bins[0])/2

def available_models():
    model_list = ['BaSTI','PARSEC','MIST','Geneva','Dartmouth','YaPSI']
    model_sources = [
        'http://basti-iac.oa-abruzzo.inaf.it/',
        'https://stev.oapd.inaf.it/PARSEC/',
        'https://waps.cfa.harvard.edu/MIST/',
        'https://www.unige.ch/sciences/astro/evolution/en/database/syclist',
        'https://rcweb.dartmouth.edu/stellar/',
        'http://www.astro.yale.edu/yapsi/'
    ]
    for model,source in zip(model_list,model_sources):
        print(model + 'Model (' + source + ')')

class AgeModel:
    def __init__(self,model_name,cut=False,use_sklearn=True,use_tqdm=True):
        self.model_name = model_name
        self.use_sklearn = use_sklearn
        self.use_tqdm = use_tqdm
        if not has_tqdm and self.use_tqdm:
            self.use_tqdm = False
        self.cut = cut
        domain_path = os.path.join(NNSA_DIR, 'domain.pkl')
        domain = pickle.load(open(domain_path, 'rb'))
        if model_name in domain:
            self.domain = domain[model_name]
            self.space_col = self.domain['spaces'][0]
            self.space_mag = self.domain['spaces'][1]
            self.space_met = self.domain['spaces'][2]
            self.domain = self.domain['grid']
        else:
            self.domain = None
            self.space_col = None
            self.space_mag = None
            self.space_met = None
        if self.cut:
            self.model_name = self.model_name + '_cut'
        self.neural_networks = {}
        self.scalers = {}
        self.samples = None
        self.ages = None
        self.medians = None
        self.means = None
        self.modes = None
        self.stds = None
        self.load_neural_network(self.model_name)

    def __str__(self):
        return self.model_name + ' Age Model'

    def load_neural_network(self, model_name):
        if self.use_sklearn:
            model_path_full = os.path.join(NNSA_DIR, 'models', f'{model_name}.sav')
            model_path_reduced = os.path.join(NNSA_DIR, 'models', f'{model_name}_BPRP.sav')
            if os.path.exists(model_path_full):
                nn = pickle.load(open(model_path_full, 'rb'))
                self.neural_networks['full'] = nn['NN']
                self.scalers['full'] = nn['Scaler']
            if os.path.exists(model_path_reduced):
                nn = pickle.load(open(model_path_reduced, 'rb'))
                self.neural_networks['reduced'] = nn['NN']
                self.scalers['reduced'] = nn['Scaler']
        else:
            model_path_full = os.path.join(NNSA_DIR, 'models', f'NN_{model_name}.json')
            model_path_reduced = os.path.join(NNSA_DIR, 'models', f'NN_{model_name}_BPRP.json')
            if os.path.exists(model_path_full):
                json_nn = json.load(open(model_path_full, 'r'))
                self.neural_networks['full'] = {
                    'weights':json_nn['weights'],
                    'biases':json_nn['biases']
                }
                self.scalers['full'] = {
                    'means':json_nn['means'],
                    'stds':json_nn['stds']
                }
            if os.path.exists(model_path_reduced):
                json_nn = json.load(open(model_path_reduced, 'r'))
                self.neural_networks['reduced'] = {
                    'weights':json_nn['weights'],
                    'biases':json_nn['biases']
                }
                self.scalers['reduced'] = {
                    'means':json_nn['means'],
                    'stds':json_nn['stds']
                }

    def ages_prediction(self,
                        met,mag,col,
                        emet=None,emag=None,ecol=None,
                        GBP=None,GRP=None,
                        eGBP=None,eGRP=None,
                        n=1,
                        store_samples=True,
                        min_age=0,max_age=14):
        
        if met is not None and type(met) is not list:
            if hasattr(met,'tolist'):
                met = met.tolist()
            else:
                met = [met]
        if mag is not None and type(mag) is not list:
            if hasattr(mag,'tolist'):
                mag = mag.tolist()
            else:
                mag = [mag]
        if col is not None and type(col) is not list:
            if hasattr(col,'tolist'):
                col = col.tolist()
            else:
                col = [col]
        if emet is not None and type(emet) is not list:
            if hasattr(emet,'tolist'):
                emet = emet.tolist()
            else:
                emet = [emet]
        if emag is not None and type(emag) is not list:
            if hasattr(emag,'tolist'):
                emag = emag.tolist()
            else:
                emag = [emag]
        if ecol is not None and type(ecol) is not list:
            if hasattr(ecol,'tolist'):
                ecol = ecol.tolist()
            else:
                ecol = [ecol]
        if GBP is not None and type(GBP) is not list:
            if hasattr(GBP,'tolist'):
                GBP = GBP.tolist()
            else:
                GBP = [GBP]
        if GRP is not None and type(GRP) is not list:
            if hasattr(GRP,'tolist'):
                GRP = GRP.tolist()
            else:
                GRP = [GRP]
        if eGBP is not None and type(eGBP) is not list:
            if hasattr(eGBP,'tolist'):
                eGBP = eGBP.tolist()
            else:
                eGBP = [eGBP]
        if eGRP is not None and type(eGRP) is not list:
            if hasattr(eGRP,'tolist'):
                eGRP = eGRP.tolist()
            else:
                eGRP = [eGRP]

        if store_samples and n*len(met) > 1e6:
            warnings.warn('Storing samples for {} stars with {} samples for each will take a lot of memory. Consider setting store_samples=False to only store mean,median,mode and std of individual age distributions.'.format(len(met),n))

        inputs = [input for input in [met,mag,col,emet,emag,ecol,GBP,GRP,eGBP,eGRP] if input is not None]
        if len(set(map(len,inputs))) != 1:
            raise ValueError('All input arrays must have the same length')

        is_reduced = True
        has_errors = False
        if GBP is not None and GRP is not None:
            is_reduced = False
            if emet is not None and emag is not None and ecol is not None and eGBP is not None and eGRP is not None:
                has_errors = True
        else:
            if emet is not None and emag is not None and ecol is not None:
                has_errors = True
        
        if n > 1 and not has_errors:
            raise ValueError('For more than one sample, errors must be provided')
        
        if is_reduced:
            X = np.array([met, mag, col])
            X_errors = np.array([emet, emag, ecol])
        else:
            X = np.array([met, mag, GBP, GRP, col])
            X_errors = np.array([emet, emag, eGBP, eGRP, ecol])

        X = X.T
        X_errors = X_errors.T

        if X.shape[1] == 3:
            if self.neural_networks.get('reduced') is None:
                raise ValueError('Reduced neural network not available for this model')
            scaler = self.scalers['reduced']
            neural_network = self.neural_networks['reduced']
        else:
            if self.neural_networks.get('full') is None:
                raise ValueError('Full neural network not available for this model')
            scaler = self.scalers['full']
            neural_network = self.neural_networks['full']

        self.ages = np.zeros((X.shape[0],n))
        if store_samples:
            self.samples = np.zeros((X.shape[0],n,X.shape[1]))
        else:
            self.samples = None
            self.medians = np.zeros(X.shape[0])
            self.means = np.zeros(X.shape[0])
            self.modes = np.zeros(X.shape[0])
            self.stds = np.zeros(X.shape[0])

        if self.use_tqdm and (n > 1 or X.shape[0] > 1):
            loop = tqdm(range(X.shape[0]))
        else:
            loop = range(X.shape[0])
        for i in loop:
            if n > 1:
                X_i = np.random.normal(X[i],X_errors[i],(n,X.shape[1]))
                if store_samples:
                    self.samples[i] = X_i
            else:
                X_i = X[i].reshape(1,-1)
                if store_samples:
                    self.samples[i] = X_i
            
            ages = self.propagate(X_i,neural_network,scaler)
            if store_samples:
                self.ages[i] = ages
            else:
                median = np.median(ages)
                mean = np.mean(ages)
                mode = get_mode(ages,min_age,max_age)
                std = np.std(ages)
                self.medians[i] = median
                self.means[i] = mean
                self.modes[i] = mode
                self.stds[i] = std

        if store_samples:
            return self.ages
        else:
            return {'mean':self.means,'median':self.medians,'mode':self.modes,'std':self.stds}

    def check_domain(self,met,mag,col,emet=None,emag=None,ecol=None):
        if self.domain is None:
            raise ValueError('No domain defined for this model')
        if met is not None and type(met) is not list:
            if hasattr(met,'tolist'):
                met = met.tolist()
            else:
                met = [met]
        if mag is not None and type(mag) is not list:
            if hasattr(mag,'tolist'):
                mag = mag.tolist()
            else:
                mag = [mag]
        if col is not None and type(col) is not list:
            if hasattr(col,'tolist'):
                col = col.tolist()
            else:
                col = [col]
        if emet is not None and type(emet) is not list:
            if hasattr(emet,'tolist'):
                emet = emet.tolist()
            else:
                emet = [emet]
        if emag is not None and type(emag) is not list:
            if hasattr(emag,'tolist'):
                emag = emag.tolist()
            else:
                emag = [emag]
        if ecol is not None and type(ecol) is not list:
            if hasattr(ecol,'tolist'):
                ecol = ecol.tolist()
            else:
                ecol = [ecol]
        
        has_errors = emet != None and emag != None and ecol != None
        
        in_domain = np.zeros(len(met),dtype=bool)

        if self.use_tqdm and len(met) > 1:
            loop = tqdm(range(len(met)))
        else:
            loop = range(len(met))

        for i in loop:
            if has_errors:
                errors = [ecol[i],emag[i],emet[i]]
            else:
                errors = [0,0,0]
            min_i_col = np.maximum(np.digitize(col[i] - errors[0],self.space_col) - 1,0)
            max_i_col = np.minimum(np.digitize(col[i] + errors[0],self.space_col) - 1,self.space_col.size-2)
            min_i_mag = np.maximum(np.digitize(mag[i] - errors[1],self.space_mag) - 1,0)
            max_i_mag = np.minimum(np.digitize(mag[i] + errors[1],self.space_mag) - 1,self.space_mag.size-2)
            min_i_met = np.maximum(np.digitize(met[i] - errors[2],self.space_met) - 1,0)
            max_i_met = np.minimum(np.digitize(met[i] + errors[2],self.space_met) - 1,self.space_met.size-2)
            #cells[i] = np.array([[min_i_col,max_i_col],[min_i_mag,max_i_mag],[min_i_met,max_i_met]])
            if self.cut and (self.space_col[min_i_col] > 1.25 or self.space_mag[min_i_mag] > 4):
                in_domain[i] = False
                continue
            in_domain[i] = bool(np.any(self.domain[min_i_col:max_i_col+1,min_i_mag:max_i_mag+1,min_i_met:max_i_met+1]) == 1)
        
        return in_domain#,cells
    
    def propagate(self,X,neural_network,scaler):
        if self.use_sklearn:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                X = scaler.transform(X)
                return neural_network.predict(X)
        else:
            weights = neural_network['weights']
            biases = neural_network['biases']
            means = scaler['means']
            stds = scaler['stds']
            outputs = []
            for x in X:
                a = (x - means)/stds
                output = self.predict_nn(a,weights,biases)
                outputs.append(output)
            return np.array(outputs)

    def relu(self,x):
        return np.maximum(0,x)

    def dot(self,x,y):
        x_dot_y = 0
        for i in range(len(x)):
            x_dot_y += x[i]*y[i]
        return x_dot_y

    def predict_nn(self,X,weights,biases):
        a = X
        for i in range(len(weights)):
            a = self.dot(a,weights[i]) + biases[i]
            a = self.relu(a)
        return a[0]
    
    def mean_ages(self):
        if self.ages is None:
            raise ValueError('No age predictions have been made yet')
        self.means = np.mean(self.ages,axis=1)
        return self.means

    def median_ages(self):
        if self.ages is None:
            raise ValueError('No age predictions have been made yet')
        self.medians = np.median(self.ages,axis=1)
        return self.medians

    def mode_ages(self):
        if self.ages is None:
            raise ValueError('No age predictions have been made yet')
        #TODO: choose number of bins appropriately
        modes = []
        min_age = max(0,self.ages.min())
        max_age = max(14,self.ages.max())

        for i in range(len(self.ages)):
            modes.append(get_mode(self.ages[i],min_age,max_age))
        self.modes = np.array(modes)
        return self.modes
    
    def std_ages(self):
        if self.ages is None:
            raise ValueError('No age predictions have been made yet')
        self.stds = np.std(self.ages,axis=1)
        return self.stds
    
class BaSTIModel(AgeModel):
    def __init__(self,cut=False,use_sklearn=True,use_tqdm=True):
        super().__init__('BaSTI',cut,use_sklearn,use_tqdm)

'''
class BaSTI2Model(AgeModel):
    def __init__(self,cut=False,use_sklearn=True,use_tqdm=True):
        super().__init__('BaSTI2',cut,use_sklearn,use_tqdm)

class BaSTI_HSTModel(AgeModel):
    def __init__(self,cut=False,use_sklearn=True,use_tqdm=True):
        super().__init__('BaSTI_HST',cut,use_sklearn,use_tqdm)

class BaSTI_HST_alpha_zeroModel(AgeModel):
    def __init__(self,cut=False,use_sklearn=True,use_tqdm=True):
        super().__init__('BaSTI_HST_alpha_zero',cut,use_sklearn,use_tqdm)
'''

class PARSECModel(AgeModel):
    def __init__(self,cut=False,use_sklearn=True,use_tqdm=True):
        super().__init__('PARSEC',cut,use_sklearn,use_tqdm)

class MISTModel(AgeModel):
    def __init__(self,cut=False,use_sklearn=True,use_tqdm=True):
        super().__init__('MIST',cut,use_sklearn,use_tqdm)

class GenevaModel(AgeModel):
    def __init__(self,cut=False,use_sklearn=True,use_tqdm=True):
        super().__init__('Geneva',cut,use_sklearn,use_tqdm)

class DartmouthModel(AgeModel):
    def __init__(self,cut=False,use_sklearn=True,use_tqdm=True):
        super().__init__('Dartmouth',cut,use_sklearn,use_tqdm)

class YaPSIModel(AgeModel):
    def __init__(self,cut=False,use_sklearn=True,use_tqdm=True):
        super().__init__('YaPSI',cut,use_sklearn,use_tqdm)

#TODO: add flavors to models (e.g. trained on cut CMD for optimal performance)
"""Rebuild report tables/figures from supplied evidence; never refits models.
Run with Python 3.10+, numpy, pandas, matplotlib. Input CSVs are bundled.
Core results retain the four-decimal precision of the notebook displays.
"""
from pathlib import Path
import os, json, csv, itertools
os.environ.setdefault('MPLCONFIGDIR', '/tmp/eurovision_mpl')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT = Path(__file__).resolve().parent
E = ROOT/'evidence'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.bbox':'tight','pdf.fonttype':42})
blue, orange = '#24638a', '#b65b28'
def read(name): return pd.read_csv(E/name)
def table(name, header, rows, fmt):
    text='\\begin{tabular}{'+fmt+'}\n\\toprule\n'+header+' \\\\\n\\midrule\n'
    text+='\n'.join(' & '.join(map(str,row))+' \\\\' for row in rows)
    text+='\n\\bottomrule\n\\end{tabular}\n'
    (ROOT/'tables'/name).write_text(text)
lift=[]
for task in 'ABC':
    metric='log_loss' if task=='C' else 'brier'
    rows=[]
    for regime,model in [('market','M0'),('core','M1'),('market','M1'),('core','M2'),('market','M2')]:
        d=read(f'{task}_{regime}_development.csv').set_index('model').loc[model]
        h=read(f'{task}_{regime}_holdout.csv').set_index('model').loc[model]
        ll='binary_log_loss' if task=='A' else 'log_loss'
        rows.append([model, 'History only' if model=='M0' else ('Without odds' if regime=='core' else 'With odds'),*[f'{v:.4f}' for v in [d.brier,d[ll],h.brier,h[ll]]]])
    table(f'results_{task}.tex','Model & Predictors & \\multicolumn{2}{c}{2021--2024 mean} & \\multicolumn{2}{c}{2025} \\\\ \n & & Brier & Log loss & Brier & Log loss',rows,'llrrrr')
    for model in ['M1','M2']:
        row=[task,model]
        for period in ['development','holdout']:
            c=read(f'{task}_core_{period}.csv').set_index('model').loc[model,metric]
            m=read(f'{task}_market_{period}.csv').set_index('model').loc[model,metric]
            lift.append(dict(task=task,model=model,period=period,metric=metric,core=c,market=m,reduction=c-m,percent=100*(c-m)/c))
pd.DataFrame(lift).to_csv(E/'market_increment.csv',index=False)
fig,axes=plt.subplots(1,3,figsize=(10.5,3.1))
for ax,task,title in zip(axes,'ABC',['A: top ten (Brier)','B: audience vs jury (Brier)','C: national winner (log loss)']):
    d=pd.DataFrame(lift);d=d[(d.task==task)&(d.period=='development')]
    x=np.arange(2)
    ax.bar(x-.18,d.core,.34,color=orange,label='Without odds')
    ax.bar(x+.18,d.market,.34,color=blue,label='With odds')
    ax.set_xticks(x,['M1','M2']);ax.set_title(title,fontsize=10);ax.set_ylim(0,max(d.core.max(),d.market.max())*1.25)
    for i,r in enumerate(d.itertuples()):
        ax.text(i,max(r.core,r.market)*1.05,f'{r.percent:+.1f}% reduction',ha='center',fontsize=8)
axes[0].set_ylabel('Mean loss, 2021–2024 (lower is better)');axes[1].legend(frameon=False,loc='lower center',bbox_to_anchor=(.5,-.38),ncol=2)
fig.tight_layout();fig.savefig(ROOT/'figures/market_increment.pdf');fig.savefig(ROOT/'figures/market_increment.png',dpi=170);plt.close(fig)
# Coefficients conditional on all predictors, trained only through 2024.
d=read('C_market_effects.csv');d=d[d.model.eq('M2')].set_index('feature').loc[['market_strength','past_pair_support','shared_border','log_distance']]
fig,ax=plt.subplots(figsize=(7,2.6));y=np.arange(len(d))
ax.errorbar(d['mean'],y,xerr=[d['mean']-d.q05,d.q95-d['mean']],fmt='o',color=blue,capsize=3)
ax.set_yticks(y,['Market strength','Past pair support','Shared land border','Log distance']);ax.invert_yaxis();ax.axvline(0,color='.6',lw=1);ax.set_xlabel('Utility coefficient: posterior mean and 90% credible interval')
fig.tight_layout();fig.savefig(ROOT/'figures/pair_effects.pdf');fig.savefig(ROOT/'figures/pair_effects.png',dpi=170);plt.close(fig)

rows=[]
for t in 'ABC':
    for model in ['M1','M2']:
        d=[r for r in lift if r['task']==t and r['model']==model]
        rows.append([t,model,*[v for r in d for v in [f"{r['reduction']:+.4f}",f"{r['percent']:+.1f}\\%"]]])
table('increment.tex','Task & Model & \\multicolumn{2}{c}{2021--2024} & \\multicolumn{2}{c}{2025} \\\\ \n & & Loss reduction & Relative & Loss reduction & Relative',rows,'llrrrr')
print(pd.DataFrame(lift).to_string(index=False))

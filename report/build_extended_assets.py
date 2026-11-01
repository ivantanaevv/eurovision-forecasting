"""Reproduce the descriptive analysis and additional evaluation figures.

Input tables are frozen in evidence/. No model fitting or image digitization.
EDA follows Untitled26 (1).ipynb, cells 3--9. Probability tables extracted
from notebook HTML retain their displayed 0.1 percentage-point precision.
Run after build_report_assets.py with numpy, pandas and matplotlib.
"""
from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/eurovision_mpl')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from matplotlib.colors import TwoSlopeNorm
ROOT = Path(__file__).resolve().parent
E, F, T = ROOT/'evidence', ROOT/'figures', ROOT/'tables'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,
    'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,
    'savefig.bbox':'tight'})
BLUE, ORANGE, GRAY, TEAL = '#24638a', '#b65b28', '#787878', '#278a74'
COLORS = {'M0':GRAY,'M1':BLUE,'M2':ORANGE}
def read(n): return pd.read_csv(E/n)
def save(fig,name):
    fig.savefig(F/(name+'.pdf'))
    fig.savefig(F/(name+'.png'),dpi=180)
    plt.close(fig)
def table(name,header,rows,fmt):
    text='\\begin{tabular}{'+fmt+'}\n\\toprule\n'+header+' \\\\\n\\midrule\n'
    text+='\n'.join(' & '.join(map(str,row))+' \\\\' for row in rows)
    (T/name).write_text(text+'\n\\bottomrule\n\\end{tabular}\n')
A,B,C,M = [read('eda_'+t+'.csv') for t in ['A','B','C','A_market']]
names=read('country_names.csv').set_index('country').country_name.to_dict()

def rates_by_year(df,group,target,order,seed=2026,draws=3000):
    stats=df.groupby(['year',group],observed=True)[target].agg(['sum','count'])
    years=np.sort(df.year.unique())
    def mat(field):
        return stats[field].unstack(group).reindex(index=years,columns=order).fillna(0).to_numpy(float)
    successes,counts=mat('sum'),mat('count')
    weights=np.random.default_rng(seed).multinomial(len(years),np.full(len(years),1/len(years)),size=draws)
    den=weights@counts
    sims=np.divide(weights@successes,den,out=np.full(den.shape,np.nan),where=den>0)
    lo,hi=np.nanquantile(sims,[.025,.975],axis=0)
    return pd.DataFrame({'rate':successes.sum(0)/counts.sum(0),'lo':lo,'hi':hi,'n':counts.sum(0).astype(int)},index=order)

# Descriptive coverage: count voting events separately from candidate rows.
coverage=pd.DataFrame({'finalists':A.groupby('year').size(),
    'top10':A.groupby('year').target_top10.sum(),
    'split_results':B.groupby('year').size(),
    'audience_above_jury':B.groupby('year').target_audience_above_jury.sum(),
    'national_votes':C.groupby('year').voter.nunique(),
    'candidate_rows':C.groupby('year').size(),
    'market_finalists':M.groupby('year').size()}).fillna(0).astype(int)
coverage.index.name='year';coverage.to_csv(E/'data_coverage_by_year.csv')
table('coverage_by_year.tex','Year & Finalists & Split ranks & Audience $>$ jury & Votes & Candidate rows & Odds',
      [[i,*map(int,r)] for i,r in coverage.drop(columns='top10').iterrows()],'rrrrrrr')
features=['running_position','bpm','danceability','dynamic_complexity','log_word_count','repetitiveness']
labels=['Running position','Tempo (BPM)','Danceability','Dynamic complexity','Log word count','Repetitiveness']
summary=A[features].describe().T
summary['missing']=A[features].isna().sum();summary.to_csv(E/'descriptive_feature_summary.csv')
table('descriptive_features.tex','Variable & Mean & SD & Q25 & Median & Q75 & Missing',
      [[lab,*[f'{r[x]:.2f}' for x in ['mean','std','25%','50%','75%']],int(r['missing'])]
       for lab,(_,r) in zip(labels,summary.iterrows())],'lrrrrrr')

# Figure: running order and the three audio variables in the supplied EDA.
pos=A.assign(position_bin=pd.cut(A.running_position,np.linspace(0,1,6),labels=False,include_lowest=True))
order=rates_by_year(pos,'position_bin','target_top10',list(range(5)))
order.to_csv(E/'eda_running_order.csv',index_label='bin')
fig,axes=plt.subplots(2,2,figsize=(9.6,6.2),layout='constrained')
ax=axes[0,0];x=np.arange(5)
ax.bar(x,order.rate,color=BLUE,width=.6)
ax.errorbar(x,order.rate,yerr=[order.rate-order.lo,order.hi-order.rate],fmt='none',color='#222222',capsize=3)
ax.axhline((10/A.n_finalists).mean(),color=GRAY,ls='--',lw=1)
ax.set_xticks(x,[f'{20*i}–{20*(i+1)}%\n(n={n})' for i,n in enumerate(order.n)])
ax.set_ylim(0,.65);ax.yaxis.set_major_formatter(PercentFormatter(1))
ax.set_ylabel('Fraction finishing in the top ten');ax.set_xlabel('Relative running position')
ax.set_title('(a) Running order')
rng=np.random.default_rng(2026)
audio=[]
for ax,col,title in zip(axes.flat[1:],['bpm','danceability','dynamic_complexity'],['(b) Tempo (BPM)','(c) Danceability','(d) Dynamic complexity']):
    groups=[A.loc[A.target_top10.eq(flag),col].to_numpy() for flag in [0,1]]
    for i,vals in enumerate(groups):
        ax.scatter(i+rng.uniform(-.16,.16,len(vals)),vals,s=8,alpha=.17,color=[GRAY,BLUE][i],edgecolor='none')
        audio.append(dict(feature=col,top10=i,n=len(vals),q25=np.quantile(vals,.25),median=np.median(vals),q75=np.quantile(vals,.75)))
    bp=ax.boxplot(groups,positions=[0,1],widths=.42,patch_artist=True,showfliers=False,
        medianprops={'color':'#111111','lw':1.5})
    for patch,color in zip(bp['boxes'],[GRAY,BLUE]):patch.set_facecolor(color);patch.set_alpha(.22)
    ax.set_xticks([0,1],[f'Other finalists\n(n={len(groups[0])})',f'Top ten\n(n={len(groups[1])})'])
    ax.set_title(title);ax.grid(axis='y',alpha=.15)
pd.DataFrame(audio).to_csv(E/'eda_audio_by_result.csv',index=False)
save(fig,'data_song_patterns')

# Country frequencies and geographic frequencies, retaining the original denominators.
country=B.groupby('country').target_audience_above_jury.agg(wins='sum',n='size')
country=country[country.n.ge(7)].copy();country['rate']=country.wins/country.n
z=1.96;den=1+z*z/country.n;center=(country.rate+z*z/(2*country.n))/den
half=z*np.sqrt(country.rate*(1-country.rate)/country.n+z*z/(4*country.n**2))/den
country['lo']=center-half;country['hi']=center+half
country=country.sort_values(['rate','n']);country.to_csv(E/'eda_country_audience.csv')
geo=C.assign(distance_km=np.expm1(C.log_distance))
geo['distance_bin']=pd.cut(geo.distance_km,[0,500,1500,3000,6000,np.inf],labels=False,include_lowest=True)
distance=rates_by_year(geo,'distance_bin','target_first_place',list(range(5)))
border=rates_by_year(geo,'shared_border','target_first_place',[0,1])
distance.to_csv(E/'eda_distance.csv',index_label='bin');border.to_csv(E/'eda_border.csv',index_label='border')
fig=plt.figure(figsize=(10,6.5),layout='constrained');gs=fig.add_gridspec(2,2,width_ratios=[1.1,1])
ax=fig.add_subplot(gs[:,0]);y=np.arange(len(country))
ax.errorbar(country.rate,y,xerr=[country.rate-country.lo,country.hi-country.rate],fmt='o',color=BLUE,capsize=2)
ax.set_yticks(y,[f'{names.get(c,c)} ({int(r.wins)}/{int(r.n)})' for c,r in country.iterrows()])
ax.axvline(.5,color=GRAY,ls='--',lw=1);ax.set_xlim(-.03,1.03)
ax.xaxis.set_major_formatter(PercentFormatter(1));ax.set_xlabel('Audience rank better than jury rank')
ax.set_title('(a) Country histories, ≥7 finals');ax.grid(axis='x',alpha=.15)
for ax,d,labs,title in [(fig.add_subplot(gs[0,1]),distance,['<500','500–\n1,500','1,500–\n3,000','3,000–\n6,000','>6,000'],'(b) Capital distance (km)'),
                       (fig.add_subplot(gs[1,1]),border,['No border','Shared border'],'(c) Shared land border')]:
    x=np.arange(len(d));ax.bar(x,d.rate,color=TEAL,width=.6)
    ax.errorbar(x,d.rate,yerr=[d.rate-d.lo,d.hi-d.rate],fmt='none',color='#222222',capsize=3)
    ax.axhline((1/C.candidate_count).mean(),color=GRAY,ls='--',lw=1)
    ax.set_xticks(x,[f'{lab}\nn={n:,}' for lab,n in zip(labs,d.n)])
    ax.set_ylim(0,.22);ax.yaxis.set_major_formatter(PercentFormatter(1));ax.set_ylabel('National first-place rate');ax.set_title(title)
save(fig,'data_country_geography')

# Full annual metric paths in the archived-odds experiment.
fig,axes=plt.subplots(3,2,figsize=(9.5,7.3),layout='constrained')
for row,t in enumerate('ABC'):
    d=read(f'{t}_market_years.csv')
    for j,(metric,label) in enumerate([('brier','Brier'),('ranking_log_loss' if t=='A' else 'log_loss','Full-ranking log loss' if t=='A' else 'Log loss')]):
        ax=axes[row,j]
        for model in ['M0','M1','M2']:
            a=d[d.model.eq(model)].sort_values('year');ax.plot(a.year,a[metric],'-o',color=COLORS[model],label=model,markersize=4)
        ax.set_title(f'{t}: {label}');ax.set_xticks([2021,2022,2023,2024]);ax.grid(axis='y',alpha=.15)
        if row==2:ax.set_xlabel('Forecast year')
axes[0,0].legend(frameon=False,ncol=3)
save(fig,'annual_market_complete')

# Supplementary scores generated from the same model exports.
rows=[]
for regime,model in [('market','M0'),('core','M1'),('market','M1'),('core','M2'),('market','M2')]:
    d=read(f'A_{regime}_development.csv').set_index('model').loc[model]
    h=read(f'A_{regime}_holdout.csv').set_index('model').loc[model]
    rows.append([model,'History' if model=='M0' else ('No odds' if regime=='core' else 'With odds'),
        f'{d.ranking_log_loss:.3f}',f'{h.ranking_log_loss:.3f}',f'{d.winner_log_loss:.3f}',f'{h.winner_log_loss:.3f}',f'{h.p_actual_winner:.4f}'])
table('A_ranking_winner.tex','Model & Predictors & \\multicolumn{2}{c}{Ranking log loss} & \\multicolumn{2}{c}{Winner log loss} & $P(\\mathrm{AT},2025)$ \\\\ \n & & 2021--24 & 2025 & 2021--24 & 2025 &',rows,'llrrrrr')
rows=[]
for regime,model in [('market','M0'),('core','M1'),('market','M1'),('core','M2'),('market','M2')]:
    d=read(f'C_{regime}_development.csv').set_index('model').loc[model]
    h=read(f'C_{regime}_holdout.csv').set_index('model').loc[model]
    rows.append([model,'History' if model=='M0' else ('No odds' if regime=='core' else 'With odds'),
        f'{100*d.accuracy:.1f}\\%',f'{100*d.top3_accuracy:.1f}\\%',
        f'{round(36*h.accuracy)}/36',f'{round(36*h.top3_accuracy)}/36'])
table('C_selection_accuracy.tex','Model & Predictors & \\multicolumn{2}{c}{2021--2024 mean} & \\multicolumn{2}{c}{2025} \\\\ \n & & Top one & Top three & Top one & Top three',rows,'llrrrr')

rows=[]
for t in 'ABC':
    d=read(f'{t}_core_sensitivity.csv')
    metric='log_loss' if t=='C' else 'brier'
    prior='prior' if t=='B' else 'prior_scale'
    for m in ['M1','M2']:
        a=d[d.model.eq(m)].set_index(prior)
        base=a.loc['original' if t=='B' else '1x',metric]
        wide=a.loc['scales_2x' if t=='B' else '2x',metric]
        rows.append([t,m,'Log loss' if t=='C' else 'Brier',f'{base:.4f}',f'{wide:.4f}',f'{wide-base:+.4f}'])
table('prior_sensitivity.tex','Task & Model & Score & Original & Double scales & Change',rows,'lllrrr')

snapshot=M[M.year.eq(2025)].sort_values('p_market',ascending=False).head(12)
snapshot.to_csv(E/'market_2025_top12.csv',index=False)
table('market_snapshot.tex','Market rank & Country & Normalized implied probability & Final place',
      [[i+1,names.get(r.country,r.country),f'{100*r.p_market:.2f}\\%',r.place_final] for i,r in enumerate(snapshot.itertuples())],'rlrr')

# M1 odds ablation at the forecast level: exact market values and rounded core display values.
fig,axes=plt.subplots(1,2,figsize=(10,7.8),layout='constrained')
prob_changes=[]
for ax,t in zip(axes,'AB'):
    core=read(f'{t}_core_comparison_2025.csv').set_index('country')
    market=read(f'{t}_market_comparison_2025.csv');market=market[market.model.eq('M1')].set_index('country')
    if t=='A':
        core=core.sort_values('place_final');pc=core.M1_p_top10;pm=market.p_top10.reindex(core.index);truth=core.place_final.le(10)
    else:
        core=core.sort_values('M1',ascending=False);pc=core.M1;pm=market.p.reindex(core.index);truth=core.target_audience_above_jury.eq(1)
    y=np.arange(len(core))
    for j,k in enumerate(core.index):
        if truth.loc[k]:ax.axhspan(j-.45,j+.45,color='#e7f2eb',zorder=0)
        ax.plot([pc.loc[k],pm.loc[k]],[j,j],color='#aeb6bd',lw=1,zorder=1)
        prob_changes.append(dict(task=t,country=k,no_odds=pc.loc[k],with_odds=pm.loc[k],actual=int(truth.loc[k])))
    ax.scatter(pc,y,facecolors='white',edgecolors=ORANGE,s=28,label='Without odds',zorder=3)
    ax.scatter(pm,y,color=BLUE,s=25,label='With odds',zorder=3)
    ax.set_yticks(y,[names.get(c,c) for c in core.index]);ax.invert_yaxis()
    ax.set_xlim(-.03,1.03);ax.xaxis.set_major_formatter(PercentFormatter(1));ax.grid(axis='x',alpha=.15)
    ax.set_xlabel('Forecast probability');ax.set_title(f'{t}: '+('Top ten, M1' if t=='A' else 'Audience above jury, M1'))
axes[0].legend(frameon=False,loc='lower right')
pd.DataFrame(prob_changes).to_csv(E/'forecast_probability_changes_2025.csv',index=False)
save(fig,'forecast_ab_2025')

# C: probability assigned to the observed national winner under M2.
core=read('C_core_comparison_2025.csv').set_index('voter')
market=read('C_market_comparison_2025.csv');market=market[market.model.eq('M2')].set_index('voter')
joined=core[['actual_winner','M2_p_actual_winner']].join(market[['p_actual_winner','predicted_winner']])
joined['change']=joined.p_actual_winner-joined.M2_p_actual_winner
joined=joined.sort_values('change',ascending=False);joined.to_csv(E/'C_probability_changes_2025.csv')
fig,ax=plt.subplots(figsize=(8.8,8.4),layout='constrained');y=np.arange(len(joined))
for j,r in enumerate(joined.itertuples()):ax.plot([r.M2_p_actual_winner,r.p_actual_winner],[j,j],color='#b6bec4',lw=1)
ax.scatter(joined.M2_p_actual_winner,y,facecolors='white',edgecolors=ORANGE,label='Without odds',s=28,zorder=3)
ax.scatter(joined.p_actual_winner,y,color=BLUE,label='With odds',s=26,zorder=3)
ax.set_yticks(y,[f'{names.get(v,v)} → {r.actual_winner}' for v,r in joined.iterrows()])
ax.invert_yaxis();ax.set_xlim(-.01,1);ax.xaxis.set_major_formatter(PercentFormatter(1));ax.grid(axis='x',alpha=.15)
ax.set_xlabel('M2 probability assigned to the actual national winner');ax.legend(frameon=False,loc='lower right')
save(fig,'forecast_c_2025')

# Calibration: distinguish the event being calibrated and show bin sample size.
fig,axes=plt.subplots(1,3,figsize=(10,3.6),layout='constrained')
for ax,t,title in zip(axes,'ABC',['A: top-ten event','B: audience above jury','C: top-choice correctness']):
    d=read(f'{t}_market_calibration.csv');ax.plot([0,1],[0,1],ls='--',lw=1,color='#999999')
    for m in ['M0','M1','M2']:
        g=d[d.model.eq(m)].sort_values('predicted');ax.plot(g.predicted,g.observed,color=COLORS[m],lw=1,label=m)
        ax.scatter(g.predicted,g.observed,s=12+g.n*1.1,color=COLORS[m],alpha=.8)
    ax.set_xlim(-.03,1.03);ax.set_ylim(-.03,1.03);ax.set_title(title)
    ax.set_xlabel('Mean forecast probability');ax.set_xticks([0,.25,.5,.75,1]);ax.grid(alpha=.12)
    ax.xaxis.set_major_formatter(PercentFormatter(1));ax.yaxis.set_major_formatter(PercentFormatter(1))
axes[0].set_ylabel('Observed frequency');axes[1].legend(frameon=False,ncol=3,loc='upper left',fontsize=8)
save(fig,'calibration_market')

# EDA regional heat map: retain all ten prespecified region countries; omit outcome-selected additions.
focus=['RU','BY','UA','MD','AM','AZ','GE','EE','LV','LT']
d=C.join(C.groupby(['year','recipient']).target_first_place.agg(total_wins='sum',total_voters='size'),on=['year','recipient'])
d['other_support']=(d.total_wins-d.target_first_place)/(d.total_voters-1)
pairs=d.groupby(['voter','recipient']).agg(wins=('target_first_place','sum'),n=('year','nunique'),other=('other_support','mean')).reset_index()
pairs['excess']=pairs.wins/pairs.n-pairs.other;pairs.to_csv(E/'eda_pair_excess.csv',index=False)
def mat(c):return pairs.pivot(index='voter',columns='recipient',values=c).reindex(index=focus,columns=focus)
vals=mat('excess');counts=mat('n');wins=mat('wins')
fig,ax=plt.subplots(figsize=(8,6.6),layout='constrained');cmap=plt.get_cmap('RdBu').copy();cmap.set_bad('#dddddd')
im=ax.imshow(vals,cmap=cmap,norm=TwoSlopeNorm(vmin=-.8,vcenter=0,vmax=.8))
ax.set_xticks(range(10),[names[c] for c in focus],rotation=45,ha='right');ax.set_yticks(range(10),[names[c] for c in focus])
ax.set_xlabel('Recipient');ax.set_ylabel('Voter')
for i in range(10):
    for j in range(10):
        if np.isfinite(vals.iloc[i,j]):
            n=int(counts.iloc[i,j]);w=int(wins.iloc[i,j]);label=f'{w}/{n}'+('*' if n<4 else '')
            ax.text(j,i,label,ha='center',va='center',fontsize=8,color='white' if abs(vals.iloc[i,j])>.45 else '#222222')
cb=fig.colorbar(im,ax=ax,shrink=.7);cb.ax.yaxis.set_major_formatter(PercentFormatter(1));cb.set_label('Difference from other voters\n(percentage points)')
save(fig,'regional_pairs')

# Aggregate national wins are sums of probabilities, not televote point totals.
d=read('C_market_predictions_2025.csv')
actual=read('C_market_comparison_2025.csv').query('model == "M0"').actual_winner.value_counts()
counts=d.groupby(['recipient','model']).p.sum().unstack().join(actual.rename('actual')).fillna(0)
counts=counts.sort_values(['actual','M2'],ascending=False);counts.to_csv(E/'C_expected_national_wins_2025.csv')
fig,ax=plt.subplots(figsize=(8.5,6.5),layout='constrained');y=np.arange(len(counts))
ax.barh(y,counts.actual,color='#dbe1e6',height=.7,label='Actual')
for model,shift in [('M0',-.19),('M1',0),('M2',.19)]:
    ax.scatter(counts[model],y+shift,color=COLORS[model],s=23,label=model,zorder=3)
ax.set_yticks(y,[names.get(c,c) for c in counts.index]);ax.invert_yaxis();ax.set_xlabel('National televote wins: expected / actual');ax.grid(axis='x',alpha=.15)
ax.legend(frameon=False,ncol=4,loc='lower right');save(fig,'national_win_counts')
print('Running order:',order.to_dict('index'))
print('Country rates:',country[['wins','n']].to_dict('index'))
print('Geography:',distance.to_dict('index'),'Border:',border.to_dict('index'))
print('Audio:',audio)
print('C expected national wins:',counts.head(8).round(3).to_dict('index'))
print('C largest changes:',joined[['actual_winner','M2_p_actual_winner','p_actual_winner']].head(3).round(4).to_dict('index'))
print('Binary missing counts:',summary['missing'].to_dict())

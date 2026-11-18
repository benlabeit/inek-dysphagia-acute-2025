"""Reproduce balanced acute figures from disclosure-checked plotted CSV.

This script does not acquire InEK data. The CSV retains the outcome, model,
population, estimate, interval and aggregate source location for every point.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import os
import sys

ROOT = Path(__file__).resolve().parent
for parent in [ROOT, *ROOT.parents]:
    candidate = parent / '.plot_deps'
    if candidate.is_dir():
        sys.path.insert(0, str(candidate))
        break
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.matplotlib_config'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.ticker import ScalarFormatter
from PIL import Image

W = 174 / 25.4
INK = '#222222'
BLUE = '#005A8D'
RUST = '#8B3D00'
GREY = '#555555'
LIGHT = '#ECECEC'
FIELDS = ['figure', 'panel', 'outcome', 'label', 'domain', 'model', 'group',
          'estimate', 'ci_lower', 'ci_upper', 'unit', 'n_total', 'n_dys',
          'n_no_dys', 'events', 'denominator', 'population', 'reference',
          'ci_method', 'source_file', 'source_key', 'status']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def configure():
    font = font_manager.findfont('Liberation Sans')
    plt.rcParams.update({'font.family': 'Liberation Sans', 'font.size': 8.5,
                         'axes.labelsize': 9, 'xtick.labelsize': 8.5,
                         'ytick.labelsize': 8.5, 'axes.linewidth': 0.7,
                         'lines.linewidth': 1.0, 'pdf.fonttype': 42,
                         'ps.fonttype': 42, 'svg.fonttype': 'none',
                         'savefig.facecolor': 'white', 'figure.facecolor': 'white'})
    return font


def clean(ax, zero=False):
    for s in ['top', 'right', 'left']:
        ax.spines[s].set_visible(False)
    ax.tick_params(axis='y', length=0, labelleft=False)
    ax.tick_params(axis='x', length=3, width=.7)
    ax.spines['bottom'].set_color(INK)
    if zero:
        ax.axvline(0, color=GREY, lw=.7, zorder=0)


def marker(ax, row, y, color=BLUE, shape='o', fill=True):
    v, lo, hi = (float(row[k]) for k in ['estimate', 'ci_lower', 'ci_upper'])
    assert lo <= v <= hi
    ax.errorbar(v, y, xerr=[[v-lo], [hi-v]], fmt='none', ecolor=color,
                capsize=2.0, elinewidth=1.05, capthick=.9, zorder=2)
    ax.plot(v, y, marker=shape, markersize=4.8,
            markerfacecolor=color if fill else 'white',
            markeredgecolor=color, markeredgewidth=1.05, ls='none', zorder=3)


def canvas_table(fig, rect, widths):
    grid = fig.add_gridspec(1, 3, left=rect[0], right=rect[1],
                            bottom=rect[2], top=rect[3],
                            width_ratios=widths, wspace=.035)
    a, b, c = [fig.add_subplot(grid[0, i]) for i in range(3)]
    for x in [a, c]:
        x.set_xlim(0, 1)
        x.axis('off')
    return a, b, c


def export(fig, stem, out):
    # Vector EPS/PDF are the submission masters. The TIFF/PNG are convenience
    # raster counterparts at 1200 dpi, satisfying the stricter line-art rule.
    fig.canvas.draw()
    files = []
    for ext in ['png', 'tiff', 'pdf', 'eps', 'svg']:
        target = out / f'{stem}.{ext}'
        kw = {'dpi': 1200}
        if ext == 'tiff':
            kw['pil_kwargs'] = {'compression': 'tiff_lzw'}
        if ext == 'pdf':
            kw['metadata'] = {'CreationDate': None, 'ModDate': None,
                              'Creator': 'Matplotlib ' + matplotlib.__version__}
        fig.savefig(target, **kw)
        if ext == 'tiff':
            with Image.open(target) as im:
                rgb = im.convert('RGB')
            rgb.save(target, compression='tiff_lzw', dpi=(1200, 1200))
        files.append(target)
    preview = out / f'{stem}_preview.png'
    fig.savefig(preview, dpi=150)
    plt.close(fig)
    return files


def group_values(rows, key):
    groups = {}
    for r in rows:
        groups.setdefault(r[key], []).append(r)
    return groups


def fig1(rows, out):
    chosen = [r for r in rows if r['figure'] == '1']
    groups = group_values(chosen, 'outcome')
    n = len(groups)
    fig = plt.figure(figsize=(W, 182 / 25.4))
    label, ax, values = canvas_table(fig, (.025, .99, .075, .92), [3.45, 3.25, 2.2])
    hi, low = n - .25, -.65
    for a in [label, ax, values]:
        a.set_ylim(low, hi)
    ax.set_xlim(-.8, 36)
    ax.set_xticks([0, 10, 20, 30])
    ax.set_xlabel('Episodes with recorded outcome (%)')
    clean(ax)
    label.text(0, 1.025, 'Clinical outcome / diagnosis code', transform=label.transAxes,
               fontsize=9, weight='bold', va='bottom')
    values.text(.24, 1.025, 'D (%)', transform=values.transAxes, fontsize=9,
                weight='bold', ha='center', va='bottom')
    values.text(.78, 1.025, 'No D (%)', transform=values.transAxes, fontsize=9,
                weight='bold', ha='center', va='bottom')
    for i, (key, rr) in enumerate(groups.items()):
        y = n - i - 1
        label.text(0, y, rr[0]['label'].replace('|', '\n'), fontsize=8.4,
                   va='center', linespacing=1.15)
        for group, shift, color, shape, fill in [('dys', .13, BLUE, 'o', True),
                                                ('no_dys', -.13, GREY, 's', False)]:
            r = next(a for a in rr if a['group'] == group)
            marker(ax, r, y+shift, color, shape, fill)
            values.text(.24 if group == 'dys' else .78, y,
                        f"{float(r['estimate']):.2f}", ha='center', va='center',
                        fontsize=8.5, color=color)
        if i < n-1:
            for a in [label, ax, values]:
                a.axhline(y-.5, color=LIGHT, lw=.45, zorder=0)
    fig.legend([Line2D([], [], ls='none', marker='o', color=BLUE, markersize=5),
                Line2D([], [], ls='none', marker='s', color=GREY,
                       markerfacecolor='white', markersize=5)],
               ['Coded dysphagia (D; n = 33,643)', 'No coded dysphagia (n = 245,634)'],
               loc='upper center', bbox_to_anchor=(.51, .995), ncol=2,
               frameon=False, fontsize=8.2, handletextpad=.4, columnspacing=1.4)
    return export(fig, 'acute_figure1', out)


def fig2(rows, out):
    chosen = [r for r in rows if r['figure'] == '2']
    groups = group_values(chosen, 'outcome')
    n = len(groups)
    fig = plt.figure(figsize=(W, min(215, 80+11*n) / 25.4))
    label, ax, values = canvas_table(fig, (.025, .99, .085, .85), [3.4, 3.2, 2.45])
    # A larger gap distinguishes procedure/process markers from clinical outcomes.
    ys = {}
    y = n-1
    previous = None
    for key, rr in groups.items():
        if previous is not None and previous != rr[0]['domain']:
            y -= .55
        ys[key] = y
        y -= 1
        previous = rr[0]['domain']
    for a in [label, ax, values]:
        a.set_ylim(y+.2, n-.2)
    ax.set_xscale('log')
    ax.set_xlim(.8, 80)
    ax.set_xticks([1, 2, 5, 10, 20, 50])
    ax.get_xaxis().set_major_formatter(ScalarFormatter())
    ax.minorticks_off()
    ax.axvline(1, color=GREY, ls='--', lw=.7, zorder=0)
    ax.set_xlabel('Standardized risk ratio (95% CI; log scale)')
    clean(ax)
    label.text(0, 1.02, 'Outcome / procedure or process code', transform=label.transAxes,
               fontsize=8.5, weight='bold', va='bottom')
    values.text(.5, 1.02, 'Age + diagnosis\nRR (95% CI)', transform=values.transAxes,
                fontsize=8.5, weight='bold', va='bottom', ha='center')
    for key, rr in groups.items():
        y = ys[key]
        label.text(0, y, rr[0]['label'].replace('|', '\n'), fontsize=8.2,
                   va='center', linespacing=1.1)
        for name, offset, color, shape, fill in [
                ('age_principal_diagnosis', .20, INK, 'o', True),
                ('age_sex_principal_diagnosis', 0, BLUE, 's', False),
                ('age_principal_diagnosis_pccl_sensitivity', -.20, RUST, '^', True)]:
            matches = [r for r in rr if r['model'] == name]
            if matches:
                marker(ax, matches[0], y+offset if len(rr)>1 else y, color, shape, fill)
        primary = next(r for r in rr if r['model'] == 'age_principal_diagnosis')
        values.text(.5, y, '{:.2f} ({:.2f}–{:.2f})'.format(
                    *[float(primary[k]) for k in ['estimate', 'ci_lower', 'ci_upper']]),
                    fontsize=8.3, va='center', ha='center')
    handles = [Line2D([], [], ls='none', marker=m, color=c,
                     markerfacecolor=c if f else 'white', markersize=5)
               for m, c, f in [('o', INK, True), ('s', BLUE, False), ('^', RUST, True)]]
    fig.legend(handles, ['Age + principal diagnosis',
                         'Age + principal diagnosis + sex',
                         'Age + principal diagnosis + PCCL (separate sensitivity)'],
               loc='upper left', bbox_to_anchor=(.24, .995), frameon=False,
               fontsize=8.2, handletextpad=.5, labelspacing=.55)
    return export(fig, 'acute_figure2', out)


def fig3(rows, out):
    los = [r for r in rows if r['figure'] == '3' and r['panel'] == 'a']
    proc = [r for r in rows if r['figure'] == '3' and r['panel'] == 'b']
    fig = plt.figure(figsize=(W, 170 / 25.4))
    label, ax, values = canvas_table(fig, (.025, .99, .52, .94), [3.8, 3.4, 2.25])
    n = len(los)
    for a in [label, ax, values]:
        a.set_ylim(-.7, n-.35)
    ax.set_xlim(0, 12)
    ax.set_xticks([0, 3, 6, 9, 12])
    ax.set_xlabel('Difference in hospital stay (days)')
    clean(ax, zero=True)
    label.text(0, 1.03, 'a', fontsize=12, weight='bold', transform=label.transAxes)
    values.text(.5, 1.03, 'Difference (95% CI)', fontsize=8.5, weight='bold',
                transform=values.transAxes, ha='center')
    for i, r in enumerate(los):
        y = n-i-1
        label.text(0, y, r['label'].replace('|', '\n'), fontsize=8.1, va='center')
        color = BLUE if 'pooled' in r['reference'] else GREY
        marker(ax, r, y, color, 'o' if 'pooled' in r['reference'] else 's',
               'pooled' in r['reference'])
        values.text(.5, y, '{:.2f} ({:.2f}–{:.2f})'.format(
                    *[float(r[k]) for k in ['estimate', 'ci_lower', 'ci_upper']]),
                    fontsize=8.2, ha='center', va='center')
        if i == 2:
            for a in [label, ax, values]:
                a.axhline(y-.5, color=GREY, ls=':', lw=.6)
    label, ax, values = canvas_table(fig, (.025, .99, .075, .355), [3.8, 3.4, 2.25])
    groups = group_values(proc, 'outcome')
    n = len(groups)
    for a in [label, ax, values]:
        a.set_ylim(-.65, n-.35)
    ax.set_xlim(-.5, 23)
    ax.set_xticks([0, 5, 10, 15, 20])
    ax.set_xlabel('Episodes with recorded procedure (%)')
    clean(ax)
    label.text(0, 1.1, 'b', fontsize=12, weight='bold', transform=label.transAxes)
    values.text(.24, 1.1, 'D (%)', fontsize=8.5, weight='bold',
                transform=values.transAxes, ha='center')
    values.text(.78, 1.1, 'No D (%)', fontsize=8.5, weight='bold',
                transform=values.transAxes, ha='center')
    for i, (key, rr) in enumerate(groups.items()):
        y = n-i-1
        label.text(0, y, rr[0]['label'].replace('|', '\n'), fontsize=8.3, va='center')
        for group, shift, color, shape, fill in [('dys', .14, BLUE, 'o', True),
                                                ('no_dys', -.14, GREY, 's', False)]:
            r = next(x for x in rr if x['group'] == group)
            marker(ax, r, y+shift, color, shape, fill)
            values.text(.24 if group == 'dys' else .78, y,
                        f"{float(r['estimate']):.2f}", ha='center', va='center',
                        fontsize=8.5, color=color)
    fig.legend([Line2D([], [], ls='none', marker='o', color=BLUE, markersize=5),
                Line2D([], [], ls='none', marker='s', color=GREY,
                       markerfacecolor='white', markersize=5)],
               ['Coded dysphagia (D)', 'No coded dysphagia'], frameon=False,
               loc='center', bbox_to_anchor=(.53, .405), ncol=2,
               fontsize=8.3, handletextpad=.5)
    return export(fig, 'acute_figure3', out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=Path, default=ROOT/'acute_harmonized_plotted_data.csv')
    parser.add_argument('--out', type=Path, default=ROOT)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    font = configure()
    with args.data.open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    assert len(rows) > 30
    for r in rows:
        assert r['status'] == 'estimated'
        assert r['source_file'] and r['source_key']
        assert float(r['ci_lower']) <= float(r['estimate']) <= float(r['ci_upper'])
    files = fig1(rows, args.out) + fig2(rows, args.out) + fig3(rows, args.out)
    files += [p for p in (args.out / ('acute_figureS1' + s) for s in ['.png','.pdf','.eps','.svg','.tiff']) if p.exists()]
    records=[]
    for p in files:
        rec={'file':p.name,'bytes':p.stat().st_size,'sha256':sha(p)}
        if p.suffix in ['.tiff','.png']:
            with Image.open(p) as im:
                rec.update({'pixels':list(im.size),'mode':im.mode,'dpi':[float(v) for v in im.info.get('dpi',[])]})
        records.append(rec)
    result={'status':'PASS','script':Path(__file__).name,'script_sha256':sha(Path(__file__)),
            'plot_data':args.data.name,'plot_data_sha256':sha(args.data),'plotted_rows':len(rows),
            'matplotlib':matplotlib.__version__,'font':plt.rcParams['font.family'][0],'resolved_font':Path(font).name,
            'width_mm':174,'font_size_range_points':[8.1,12],
            'minimum_line_width_points':.45,'raster_dpi':1200,
            'dimensions_mm':{'figure1':[174,182],'figure2':[174,min(215,80+11*len({r['outcome'] for r in rows if r['figure']=='2'}))],'figure3':[174,170],'figureS1':[174,116]},
            'vector_masters':['EPS','PDF'],'files':records,
            'notes':['All points are from disclosed aggregate outputs, not imputed cells.',
                     'RRs use a logarithmic axis; clinical diagnoses and care processes are distinguished.',
                     'Sex and PCCL models are separate; no four-factor model is plotted.',
                     'Figure S1 is preserved from the previously approved mortality figure; its vector masters and original 600-dpi raster files are unchanged.']}
    (args.out/'figure_build_manifest.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS','figures':3,'files':len(files),'rows':len(rows)},indent=2))


if __name__ == '__main__':
    main()

import bisect
import collections
import itertools
import math
import tempfile
from datetime import datetime
from functools import partial
from typing import Callable, Iterable, List, Mapping, Optional, Tuple

import pygal.config
import pygal.formatters
import pygal.serie
import pygal.style
import pygal.util


__all__ = 'Point', 'decimate', 'moving_average', 'plot'

Point = Tuple[float, float]


def get_line_distance(p0: Point, p1: Point, p2: Point) -> float:
    """
    Return the distance from p0 to the line formed by p1 and p2.

    Points are represented by 2-tuples.
    """

    if p1 == p2:
        return math.hypot(p1[0] - p0[0], p1[1] - p0[1])

    slope_nom = p2[1] - p1[1]
    slope_denom = p2[0] - p1[0]

    return (
        abs(slope_nom * p0[0] - slope_denom * p0[1] + p2[0] * p1[1] - p2[1] * p1[0])
        / math.hypot(slope_denom, slope_nom)
    )


def decimate(points: List[Point], epsilon: float) -> List[Point]:
    """
    Decimate given poly-line using Ramer-Douglas-Peucker algorithm.

    It reduces the points to a simplified version that loses detail,
    but retains its peaks.
    """

    if len(points) < 3:
        return points

    dist_iter = map(partial(get_line_distance, p1=points[0], p2=points[-1]), points[1:-1])
    max_index, max_value = max(enumerate(dist_iter, start=1), key=lambda v: v[1])

    if max_value > epsilon:
        return (
            decimate(points[:max_index + 1], epsilon)[:-1]
            + decimate(points[max_index:], epsilon)
        )
    else:
        return [points[0], points[-1]]


def moving_average(points: Iterable[Point], n: int) -> Iterable[Point]:
    """
    Calculate moving average time series of given time series.

    The average is taken from an equal number of points on either side
    of a central value. This ensures that variations in the average are
    aligned with the variations in the data rather than being shifted
    in time. ``n // 2`` values are skipped from either side of the
    series. It is equivalent of::

        df = pandas.DataFrame(points, columns=('x', 'y'))
        df.y = df.y.rolling(window=n, center=True).mean()
        df.dropna()

    """

    assert n > 0, 'n must be a positive number'

    x_series, y_series = itertools.tee(points, 2)
    x_series = itertools.islice(x_series, n // 2, None)

    d = collections.deque(y_point[1] for y_point in itertools.islice(y_series, n - 1))
    d.appendleft(0)
    s = sum(d)
    for x_point, y_point in zip(x_series, y_series):
        s += y_point[1] - d.popleft()
        d.append(y_point[1])
        yield x_point[0], s / n


class CompactXLabelDateTimeLine(pygal.DateTimeLine):  # type: ignore[module-attr]

    def _compute_x_labels(self):
        """Override to make compact X labels -- no repetition of dates."""

        super()._compute_x_labels()

        if self.relative_time:
            return

        last_date_str = None
        for i, (ts_str, ts) in enumerate(self._x_labels):
            if last_date_str == ts_str[:10]:
                self._x_labels[i] = ts_str[11:], ts

            last_date_str = ts_str[:10]


class DateTimeDotLine(CompactXLabelDateTimeLine):
    """
    An override of Pygal's date-time line chart that adds a few dots.

    It displays dots on each serie's line close to its intersection
    with X axis' labels. Dots show a tooltip on hover with the exact
    value and series name.
    """

    _dot_class = 'dot reactive tooltip-trigger'

    def __init__(self, config=None, **kwargs):
        super().__init__(config, **kwargs)

        # Disable default Pygal dots.
        self.config.show_dots = False

    def _get_x_label_view_points(
        self, serie: pygal.serie.Serie, rescale: bool
    ) -> Iterable[Tuple[int, Point]]:
        if rescale and self.secondary_series:
            points = self._rescale(serie.points)
        else:
            points = serie.points

        # Note that Pygal BaseGraph.prepare_values aligns with None
        # values all series on the respective axis to have the same
        # number of values
        safe_index_points = [(i, p) for i, p in enumerate(points) if p[0] is not None]
        # It is assumed that the X values are chronologically ordered
        safe_x_range = [t[1][0] for t in safe_index_points]

        # Note that dictionaries retain insertion order, so it can
        # be used here for deduplication
        label_points = {}
        for _, ts in self._x_labels:
            safe_index = bisect.bisect_left(safe_x_range, ts)
            if safe_index < len(safe_index_points):
                point_index, point = safe_index_points[safe_index]
                label_points[point_index] = point

        for i, (x, y) in zip(label_points.keys(), map(self.view, label_points.values())):
            if None in (x, y):
                continue
            elif self.logarithmic and (points[i][1] is None or points[i][1] <= 0):
                continue

            yield i, (x, y)

    def _draw_x_label_dots(
        self, serie: pygal.serie.Serie, view_points: Iterable[Tuple[int, Point]]
    ):
        serie_node = self.svg.serie(serie)
        for i, (x, y) in view_points:
            metadata = serie.metadata.get(i)
            dots = pygal.util.decorate(
                self.svg,
                self.svg.node(serie_node['overlay'], class_='dots'),
                metadata
            )

            val = self._format(serie, i)
            circle = self.svg.transposable_node(
                dots, 'circle', cx=x, cy=y, r=serie.dots_size, class_=self._dot_class
            )
            pygal.util.alter(circle, metadata)
            self._tooltip_data(dots, val, x, y, xlabel=self._get_x_label(i))
            self._static_value(
                serie_node,
                val,
                x + self.style.value_font_size,
                y + self.style.value_font_size,
                metadata,
            )

    def line(self, serie, rescale=False):
        """Override to plot dots at around X label intersections."""

        super().line(serie, rescale)

        view_points = self._get_x_label_view_points(serie, rescale)
        self._draw_x_label_dots(serie, view_points)


class PlottingConfig(pygal.config.Config):
    """The Pygal way to add custom attribute on a Graph instance."""

    relative_time = pygal.config.Key(False, bool, 'Value', 'Display X axis as timedeltas')


def format_x_value_absolute(v: Optional[datetime]) -> str:
    s = v.isoformat() if v is not None else ''
    s = s.rstrip('0') if '.' in s else s
    return s


def format_x_value_relative(start: datetime, v: Optional[datetime]) -> str:
    delta = str(v - start) if v is not None else ''
    delta = delta.rstrip('0') if '.' in delta else delta
    return delta


def get_x_value_formatter(
    pid_series_list: List[Mapping[int, List[Point]]], config: pygal.config.Config
) -> Callable[[Optional[datetime]], str]:
    if not config.relative_time:
        return format_x_value_absolute

    # Points are expected to be ordered in each serie so it sufficient
    # to take the first and the last
    x_min = min(
        min(points[0][0] for points in pid_series.values())
        for pid_series in pid_series_list
    )
    x_max = max(
        max(points[-1][0] for points in pid_series.values())
        for pid_series in pid_series_list
    )
    # Use PyGal's X scale for the first timedelta tick to be exactly 0
    x_scale: List[float] = pygal.util.compute_scale(
        x_min,
        x_max,
        config.logarithmic,
        config.order_min,
        config.min_scale,
        config.max_scale,
    )
    start = datetime.utcfromtimestamp(x_scale[0])
    return partial(format_x_value_relative, start)


def plot(
    pid_series_list: List[Mapping[int, List[Point]]],
    queries: list,
    plot_file: str,
    *,
    title: Optional[str] = None,
    style: Optional[str] = None,
    formatter: Optional[str] = None,
    share_y_axis: bool = False,
    logarithmic: bool = False,
    no_dots: bool = False,
    relative_time: bool = False,
):
    assert pid_series_list and len(pid_series_list) == len(queries), 'Series must match queries'
    assert share_y_axis or len(pid_series_list) <= 2, 'Only one Y axis allowed with share_y_axis'

    if not title:
        if share_y_axis:
            title = '; '.join(f'{i}. {q.title}' for i, q in enumerate(queries, start=1))
        elif len(queries) == 1:
            title = queries[0].title
        else:
            title = f'{queries[0].title} vs {queries[1].title}'

    with tempfile.NamedTemporaryFile('w') as f:
        f.write(_ui_js)
        f.flush()

        line_cls = CompactXLabelDateTimeLine if no_dots else DateTimeDotLine
        datetimeline = line_cls(
            width=912,
            height=684,
            show_dots=False,
            logarithmic=logarithmic,
            x_label_rotation=35,
            title=title,
            value_formatter=getattr(pygal.formatters, formatter or 'human_readable'),
            style=getattr(pygal.style, style or 'DefaultStyle'),
            no_prefix=True,
            js=[f'file://{f.name}'],  # embed "svg/ui.py" converted to JavaScript
            config=PlottingConfig,
            relative_time=relative_time,
        )
        datetimeline.config.x_value_formatter = get_x_value_formatter(
            pid_series_list, datetimeline.config
        )
        datetimeline.config.css.append(f'inline:{_ui_css}')
        datetimeline.config.style.tooltip_font_size = 11

        for i, (query, pid_series) in enumerate(zip(queries, pid_series_list)):
            for pid, points in pid_series.items():
                datetimeline.add(
                    '{name} {pid}'.format(pid=pid, name=query.name or f'№{i + 1}'),
                    points,
                    secondary=not share_y_axis and bool(i),
                )

        datetimeline.render_to_file(plot_file)


_ui_css = '''
.tooltip text.legend {font-size: 1em}
.tooltip text.value {font-size: 1.2em}
'''

_ui_js = (
    r'var e,t;function i(e){return e.set_properties=function(e,t){var i,s,n=t;for(var o in n)'
    r'n.hasOwnProperty(o)&&(i=!((s=t[o])instanceof Map||s instanceof WeakMap)&&s instanceof O'
    r'bject&&"get"in s&&s.get instanceof Function?s:{value:s,enumerable:!1,configurable:!0,wr'
    r'itable:!0},Object.defineProperty(e.prototype,o,i))},e}function*s(e){var t;t=0;for(var i'
    r',s=0,n=e,o=n.length;s<o;s+=1)i=n[s],yield[t,i],t+=1}function n(e,t=null){var i;return t'
    r'=t||window.document,i=[...t.querySelectorAll(e)],function(){for(var e=[],s=i,n=0,o=s.le'
    r'ngth;n<o;n+=1){var r=s[n];r!==t&&e.push(r)}return e}.call(this)}function o(e,t){return '
    r'function(){for(var i=[],s=e.parentElement.children,n=0,o=s.length;n<o;n+=1){var r=s[n];'
    r'r===e||t&&!r.matches(t)||i.push(r)}return i}.call(this)}function r(e){var i,s;return i='
    r't.exec,s=i.call(t,e.getAttribute("transform"))||[],function(){for(var e=[],t=[...s].sli'
    r'ce(1),i=0,n=t.length;i<n;i+=1){var o=t[i];e.push(Number.parseInt(o))}return e}.call(thi'
    r's)}i(e={}),t=new RegExp("translate\\((\\d+)[ ,]+(\\d+)\\)");class l{constructor(e,t){va'
    r'r i;this._chartNode=e,t.no_prefix?this._config=t:(i=e.id.replace("chart-",""),this._con'
    r'fig=t[i]),this._tooltipElement=n(".tooltip",e)[0],this._setConverters(),this._setToolti'
    r'pTriggerListeners(),this._setTooltipListeners(),this._setGraphListeners(),this._setNode'
    r'Listeners()}_setConverters(){var e,t,i,s;(s=n("svg",this._chartNode)).length?(i=s[0].pa'
    r'rentElement,t=s[0].viewBox.baseVal,e=i.getBBox(),this._xconvert=i=>(i-t.x)/t.width*e.wi'
    r'dth,this._yconvert=i=>(i-t.y)/t.height*e.height):this._xconvert=this._yconvert=e=>e}_on'
    r'GraphMouseMove(e){!this._tooltipTimeoutHandle&&e.target.matches(".background")&&this.hi'
    r'de(1e3)}_setGraphListeners(){n(".graph",this._chartNode)[0].addEventListener("mousemove'
    r'",(e=>this._onGraphMouseMove(e)))}_onNodeMouseLeave(){this._tooltipTimeoutHandle&&(wind'
    r'ow.clearTimeout(this._tooltipTimeoutHandle),this._tooltipTimeoutHandle=null),this.hide('
    r')}_setNodeListeners(){this._chartNode.addEventListener("mouseleave",(()=>this._onNodeMo'
    r'useLeave()))}_setTooltipTriggerListener(e){e.addEventListener("mouseenter",(()=>this.sh'
    r'ow(e)))}_setTooltipTriggerListeners(){for(var e,t=0,i=n(".tooltip-trigger",this._chartN'
    r'ode),s=i.length;t<s;t+=1)e=i[t],this._setTooltipTriggerListener(e)}_onTooltipMouseEnter'
    r'(){this._tooltipElement&&this._tooltipElement.classList.remove("active")}_onTooltipMous'
    r'eLeave(){this._tooltipElement&&this._tooltipElement.classList.remove("active")}_setTool'
    r'tipListeners(){this._tooltipElement.addEventListener("mouseenter",(()=>this._onTooltipM'
    r'ouseEnter())),this._tooltipElement.addEventListener("mouseleave",(()=>this._onTooltipMo'
    r'useLeave()))}_getSerieIndex(e){var t,i,s;for(i=null,t=e,s=[];t&&(s=[...s,t],!t.classLis'
    r't.contains("series"));)t=t.parentElement;if(t)for(var n,o=0,r=t.classList,l=r.length;o<'
    r'l;o+=1)if((n=r[o]).startsWith("serie-")){i=Number.parseInt(n.replace("serie-",""));brea'
    r'k}return i}_createTextGroup(e,t){var i,s,o,r,l,a,h,d,c;(h=n("g.text",this._tooltipEleme'
    r'nt)[0]).innerHTML="",o=0,d={};for(var _,p=0,u=e,v=u.length;p<v;p+=1)_=u[p],[r,l]=_,r&&('
    r'(a=window.document.createElementNS(this.svg_ns,"text")).textContent=r,a.setAttribute("x'
    r'",this.padding),a.setAttribute("dy",o),a.classList.add(l.startsWith("value")?"value":l)'
    r',l.startsWith("value")&&this._config.tooltip_fancy_mode&&a.classList.add(`color-${t}`),'
    r'"xlink"===l?((i=window.document.createElementNS(this.svg_ns,"a")).setAttributeNS(this.x'
    r'link_ns,"href",r),i.textContent="",i.appendChild(a),a.textContent="Link >",h.appendChil'
    r'd(i)):h.appendChild(a),o+=a.getBBox().height+this.padding/2,s=this.padding,a.style.domi'
    r'nantBaseline?a.style.dominantBaseline="text-before-edge":s+=.8*a.getBBox().height,a.set'
    r'Attribute("y",s),d[l]=a);return c=h.getBBox().width+2*this.padding,d.value&&d.value.set'
    r'Attribute("dx",(c-d.value.getBBox().width)/2-this.padding),d.x_label&&d.x_label.setAttr'
    r'ibute("dx",c-d.x_label.getBBox().width-2*this.padding),d.xlink&&d.xlink.setAttribute("d'
    r'x",c-d.xlink.getBBox().width-2*this.padding),h}_constrainTooltip(e,t,i,s){var n,o;retur'
    r'n[n,o]=r(this._tooltipElement.parentElement),e+i+n>this._config.width&&(e=this._config.'
    r'width-i-n),t+s+o>this._config.height&&(t=this._config.height-s-o),e+n<0&&(e=-n),t+o<0&&'
    r'(t=-o),[e,t]}_getTooltipCoordinates(e,t,i){var s,n,r,l;return n=o(e,".x")[0],l=o(e,".y"'
    r')[0],s=Number.parseInt(n.textContent),n.classList.contains("centered")?s-=t/2:n.classLi'
    r'st.contains("left")?s-=t:n.classList.contains("auto")&&(s=this._xconvert(e.getBBox().x+'
    r'e.getBBox().width/2)-t/2),r=Number.parseInt(l.textContent),l.classList.contains("center'
    r'ed")?r-=i/2:l.classList.contains("top")?r-=i:l.classList.contains("auto")&&(r=this._yco'
    r'nvert(e.getBBox().y+e.getBBox().height/2)-i/2),this._constrainTooltip(s,r,t,i)}_getTool'
    r'tipKeyMap(e,t){var i,n,r,l,a,h,d,c;n=[[(r=o(e,".label")).length?r[0].textContent:"","la'
    r'bel"]];for(var _,p=0,u=[...s(o(e,".value")[0].textContent.split("\n"))],v=u.length;p<v;'
    r'p+=1)_=u[p],[i,l]=_,n=[...n,[l,`value-${i}`]];return d=(c=o(e,".xlink")).length?c[0].te'
    r'xtContent:"",a=(h=o(e,".x_label")).length?h[0].textContent:"",this._config.tooltip_fanc'
    r'y_mode&&(n=[[t,"legend"],[a,"x_label"],...n,[d,"xlink"]]),n}show(e){var t,i,s,o,l,a,h,d'
    r',c,_,p;window.clearTimeout(this._tooltipTimeoutHandle),this._tooltipTimeoutHandle=null,'
    r'this._tooltipElement.style.opacity=1,this._tooltipElement.style.display="",l=null,null!'
    r'==(h=this._getSerieIndex(e))&&(l=this._config.legends[h]),o=this._getTooltipKeyMap(e,l)'
    r',c=(d=this._createTextGroup(o,h)).getBBox().width+2*this.padding,s=d.getBBox().height+2'
    r'*this.padding,(a=n("rect",this._tooltipElement)[0]).setAttribute("width",c),a.setAttrib'
    r'ute("height",s),[_,p]=this._getTooltipCoordinates(e,c,s),[t,i]=r(this._tooltipElement),'
    r't===_&&i===p||this._tooltipElement.setAttribute("transform",`translate(${_} ${p})`)}_hi'
    r'deDelayed(){this._tooltipElement.style.display="none",this._tooltipElement.style.opacit'
    r'y=0,this._tooltipElement.classList.remove("active"),this._tooltipTimeoutHandle=null}hid'
    r'e(e=0){this._tooltipTimeoutHandle=window.setTimeout((()=>this._hideDelayed()),e)}}e.set'
    r'_properties(l,{_chartNode:null,_config:null,_tooltipElement:null,_tooltipTimeoutHandle:'
    r'null,_xconvert:null,_yconvert:null,padding:5,svg_ns:"http://www.w3.org/2000/svg",xlink_'
    r'ns:"http://www.w3.org/1999/xlink"});class a{constructor(e){this._node=e,this._setActive'
    r'SeriesListeners()}_onActiveSerieMouseEnter(e){for(var t=0,i=(s=n(`.serie-${e} .reactive'
    r'`,this._node)).length;t<i;t+=1)s[t].classList.add("active");var s;for(t=0,i=(s=n(`.seri'
    r'e-${e} .showable`,this._node)).length;t<i;t+=1)s[t].classList.add("shown")}_onActiveSer'
    r'ieMouseLeave(e){for(var t=0,i=(s=n(`.serie-${e} .reactive`,this._node)).length;t<i;t+=1'
    r')s[t].classList.remove("active");var s;for(t=0,i=(s=n(`.serie-${e} .showable`,this._nod'
    r'e)).length;t<i;t+=1)s[t].classList.remove("shown")}_isSerieVisible(e){return!n(`#activa'
    r'te-serie-${e} rect`,this._node)[0].style.fill}_setSerieVisible(e,t){n(`#activate-serie-'
    r'${e} rect`,this._node)[0].style.fill=t?"":"transparent";for(var i=0,s=(o=n(`.serie-${e}'
    r' .reactive`,this._node)).length;i<s;i+=1)o[i].style.display=t?"":"none";var o;for(i=0,s'
    r'=(o=n(`.text-overlay .serie-${e}`,this._node)).length;i<s;i+=1)o[i].style.display=t?"":'
    r'"none"}_onActiveSerieClick(e,t){var i,s;if(s=!this._isSerieVisible(e),this._setSerieVis'
    r'ible(e,s),2===t.detail){i=!0;for(var n=0,o=this._serie_count;n<o;n+=1)n!==e&&(i=i&&!thi'
    r's._isSerieVisible(n));this._setSerieVisible(e,!0);for(n=0,o=this._serie_count;n<o;n+=1)'
    r'n!==e&&this._setSerieVisible(n,i)}}_setActiveSerieListeners(e,t){e.addEventListener("mo'
    r'useenter",(()=>this._onActiveSerieMouseEnter(t))),e.addEventListener("mouseleave",(()=>'
    r'this._onActiveSerieMouseLeave(t))),e.addEventListener("click",(e=>this._onActiveSerieCl'
    r'ick(t,e)))}_setActiveSeriesListeners(){for(var e,t,i=0,s=n(".activate-serie",this._node'
    r'),o=s.length;i<o;i+=1)t=s[i],e=Number.parseInt(t.id.replace("activate-serie-","")),this'
    r'._setActiveSerieListeners(t,e);this._serie_count=e+1}}function h(){if(!("pygal"in windo'
    r'w)||!("config"in window.pygal))throw new Error("No config defined");for(var e,t=0,i=n("'
    r'.pygal-chart"),s=i.length;t<s;t+=1)e=i[t],new a(e),new l(e,window.pygal.config)}e.set_p'
    r'roperties(a,{_node:null,_serie_count:0}),"loading"!==window.document.readyState?h():win'
    r'dow.document.addEventListener("DOMContentLoaded",h);'
)

# Carbon Budget Consistent Net Zero Scenario

In *Figure 1*, we show the annual and cumulative emissions of the NGFS GCAM6.0 “current policy” scenario and the “net-zero 2050” scenario applied to the emission values of power plants from the Forward Analytics data, and compare that against the 50%–67% range of the remaining carbon budget for each degree of warming (*Table 1*).

___
**Figure 1: The annual (left) and cumulative (right) energy-related emissions under the NGFS GCAM6.0 current policy scenario (top) and net zero 2050 scenario (bottom) relative to the 50%-67% remaining carbon budgets for each tenth of a degree of global warming.**
![Alt text](https://github.com/panahovf/ngfsanalysis/blob/277dc6b3dd7da7a59732b42a1a9c23be3e379f42/images/ngfs%20scenario%20vs%20carbon%20budget.png)
___


**Table 1: Remaining Carbon Budgets as of January 1 2024**[^1]
|     Degrees of warming           | **17%**      | **33%**      | **50%**               | **67%**      | **83%**      |
|----------------|--------------|--------------|-----------------------|--------------|--------------|
| **1.5 °C**     | 758 (900)    | 508 (650)    | 358 (500)         | 258 (400)    | 158 (300)    |
| **1.6 °C**     | 1058 (1200)  | 708 (850)    | 508 (650)             | 408 (550)    | 258 (400)    |
| **1.7 °C**     | 1308 (1450)  | 908 (1050)   | 708 (850)             | 558 (700)    | 408 (550)    |
| **1.8 °C**     | 1608 (1750)  | 1208 (1250)  | 858 (1000)            | 708 (850)    | 508 (650)    |
| **1.9 °C**     | 1858 (2000)  | 1308 (1450)  | 858 (1200)            | 858 (1000)   | 658 (800)    |
| **2 °C**       | 2158 (2300)  | 1558 (1700)  | 1208 (1350)           | 1008 (1150)  | 758 (900)    |
___


Taking into account that an emission overshoot is risky and the possibility of large negative emissions after 2050 remains as yet unproven (and are therefore not assumed beyond 2050), we observe in *Figure 1* that the NGFS scenario projects that the cumulative emissions by 2050 under current policies are estimated to bake in a warming potential to lead to 2°C global warming by 2100. We also observe that the NGFS net zero 2050 scenario is estimated not to succeed (barring an emission overshoot and large negative emissions after 2050) in limiting global warming to 1.5°C, either with 50% probability or 67% probability. Instead, the cumulative emissions by 2050 under the NGFS net zero 2050 scenario are estimated to lead to 1.6°C warming by 2100.


The question thus is how to make the NGFS net-zero 2050 scenario consistent with the remaining 1.5°C 50% carbon budget, as 1.5°C is deemed by climate scientists to represent a physical limit beyond which several climate tipping points will likely be crossed and climate extremes will become much more severe. More generally, our method presented below enables one to make any net-zero scenario (e.g., from the IEA or IPCC) consistent with the remaining carbon budget for any chosen maximum degree of global warming (e.g., 1.6°C) with a certain probability (e.g., 67%).

We observe from *Table 2* that the NGFS net zero 2050 scenario overshoots the remaining carbon budget to limit global warming by at least 31% (or more given the further depleted carbon budgets).

___
**Table 2: Overshoot (if > 1) of the cumulative 2025–2050 emissions under the NGFS Net Zero 2050 scenario relative to the remaining carbon budget associated with different temperatures (rows) and different probabilities (columns).**

| Temperature Increase | Probability 50% | Probability 67% |
|----------------------|-----------------|-----------------|
| 1.5°C                | 1.31            | 1.82            |
| 1.6°C                | 0.92            | 1.15            |
| 1.7°C                | 0.66            | 0.84            |
| 1.8°C                | 0.55            | 0.66            |
| 1.9°C                | 0.41            | 0.55            |
| 2.0°C                | 0.39            | 0.47            |
___


While there could be a number of approaches to align total cumulative emissions with the global remaining carbon budget, we choose to adjust all countries and all fossil fuel types (coal, oil, gas) at each time by the same increased decarbonization rate, \( r > 1 \). This approach allows us to maintain relative country \( y \), fuel \( f \), and time \( t \) specific pathways originally modeled by the NGFS GCAM6 model, thus retaining the richness of the original modeling framework.

In our algorithm to make the net zero 2050 scenario carbon budget consistent, we apply the following assumptions:

1. The same reduction factor \( r \) is applied to annual change rates for all fossil fuel types, in all countries, at each time of the decarbonization horizon.
2. Annual change rates are capped at -100% to ensure that no negative values occur.
3. In the original NGFS model, some countries can experience an intermediary phase-out with later re-introduction of the fossil fuels in their power or extraction sectors. We assume that in this edge case, the associated CO₂ emissions of reintroducing fossil fuels are of the same level as the NGFS emission level S<sup>s<sub>level</sub>, e</sup><sub>y, f, t</sub> under scenario \( s \), as you cannot divide by zero in equation X for E<sub>y,f,t-1</sub><sup>s₂</sup> = 0. 
4. Positive annual change rates are reduced by the same factor to maintain balance between countries reducing their fossil fuel emissions and those increasing them.
We first pick a range of values for possible decarbonization rates \( r > 1 \). Since the emission overshoot for the 1.5°C 50% remaining carbon budget is 31%, a reasonable range and step size is:


<div align="center">
r<sub>max</sub> = 31% * 10
</div>
<div align="center">
r<sub>min</sub> = 31% / 10
</div>
<div align="center">
Step size = 0.001
</div>
<br>


The relative emission reduction under the net zero 2050 scenario s<sub>2</sub> are given by:


<div align="center">
  <u>&Delta;</u> E<sup>s<sub>2</sub></sup><sub>y,f,&tau;</sub> = ( E<sup>s<sub>2</sub></sup><sub>y,f,&tau;</sub> - E<sup>s<sub>2</sub></sup><sub>y,f,&tau;-1</sub> ) / E<sup>s<sub>2</sub></sup><sub>y,f,&tau;-1</sub> =
</div>
<br>
<div align="center">
&isin; (0, -1], &nbsp;&nbsp; if E<sup>s<sub>2</sub></sup><sub>y,f,&tau;</sub> &lt; E<sup>s<sub>2</sub></sup><sub>y,f,&tau;-1</sub>
</div>
<div align="center">
&ge; 1, &nbsp;&nbsp; if E<sup>s<sub>2</sub></sup><sub>y,f,&tau;</sub> &ge; E<sup>s<sub>2</sub></sup><sub>y,f,&tau;-1</sub>
</div>
<br>


for a s<sub>2</sub> scenario absent negative emissions (as the NGFS power sector net zero 2050 scenario applied to our data is).


Under the 1.5°C 50% carbon budget consistent net zero scenario s<sub>3</sub>, we update the relative emission reduction under the net zero 2050 scenario s<sub>2</sub> to:


<div align="center">
  <u>&Delta;</u> E<sup>s<sub>3</sub></sup><sub>y,f,&tau;</sub> =
</div>
<br>
<div align="center">
max(<u>&Delta;</u> E<sup>s<sub>2</sub></sup><sub>y,f,&tau;</sub> &times; r, -1 ), &nbsp;&nbsp; if <u>&Delta;</u> E<sup>s<sub>2</sub></sup><sub>y,f,&tau;</sub> &lt; 0
</div>
<div align="center">
(<u>&Delta;</u> E<sup>s<sub>2</sub></sup><sub>y,f,&tau;</sub> / r), &nbsp;&nbsp; if <u>&Delta;</u> E<sup>s<sub>2</sub></sup><sub>y,f,&tau;</sub> &ge; 0
</div>
<br>


To obtain the 1.5°C 50% carbon budget consistent s<sub>3</sub> emission pathway E<sup>s<sub>3</sub></sup><sub>y,f,t</sub>, for each &tau; ∈ (t, T], we iteratively apply:


<div align="center">
1 + <u>&Delta;</u> E<sup>s<sub>3</sub></sup><sub>y,f,&tau;</sub>
</div>
<br>


to the initial emissions E<sup>data</sup><sub>y,f,t</sub> as given by the Forward Analytics data for \( t = 2024 \) (or IEA data for overall energy-related emissions). To get the E<sup>s<sub>3</sub></sup><sub>y,f,t+1</sub> emission under the s<sub>3</sub> pathway, we do:


<div align="center">
E<sup>s<sub>3</sub></sup><sub>y,f,t+1</sub> = E<sup>data</sup><sub>y,f,t</sub> &times; ∏<sub>&tau;=t+1</sub><sup>t+1</sup> (1 + <u>&Delta;</u> E<sup>s<sub>3</sub></sup><sub>y,f,&tau;</sub>)
</div>
<br>


More generally, to get the &tau; ∈ (t, T] emission under the s<sub>3</sub> pathway (e.g., for \( \tau = t+3 \)), we do:


<div align="center">
E<sup>s<sub>3</sub></sup><sub>y,f,&tau;</sub> = E<sup>data</sup><sub>y,f,t</sub> &times; ∏<sub>s=t+1</sub><sup>&tau;</sup> (1 + <u>&Delta;</u> E<sup>s<sub>3</sub></sup><sub>y,f,s</sub>)
</div>
<br>


Summing up the emissions over \( [t=2024, T=2050] \) gives the cumulative emissions that the s<sub>3</sub> pathway generates:


<div align="center">
E<sup>s<sub>3</sub></sup><sub>y,f,t,T</sub> = ∑<sub>&tau;=t</sub><sup>T</sup> E<sup>s<sub>3</sub></sup><sub>y,f,&tau;</sub>.
</div>
<br>


The algorithm ends when there is a reduction factor \( r \) that satisfies the condition


<div align="center">
CB - 1% &times; CB &nbsp; &le; &nbsp; ∑<sub>y ∈ 𝒴</sub> ∑<sub>f ∈ 𝒻</sub> E<sup>s<sub>3</sub></sup><sub>y,f,t,T</sub> &nbsp; &le; &nbsp; CB + 1% &times; CB,
</div>
<br>


where cumulative total energy emissions are aligned with the carbon budget (CB) for limiting global warming to 1.5°C with 50% likelihood within a 1% range.


We find \( r = 1.79 \). As you can see from the above equation, one can flexibly choose another carbon budget to align the scenario with, and indeed pick another s<sub>2</sub> scenario to start with (i.e., before making the carbon budget adjustment).


For the purposes of the above algorithm, we referred to the carbon-budget aligned scenario, adapted from scenario s<sub>2</sub>, as s<sub>3</sub>. However, in the remainder of the paper we will simply refer to this as scenario s<sub>2</sub>.


___
**Figure 2: 1.5°C 50% Carbon Budget Consistent Net Zero Scenario**
**Annual (left plot) and cumulative (right plot) emissions under the "1.5°C 50% carbon budget consistent net zero" scenario.**
![Alt text](https://github.com/panahovf/ngfsanalysis/blob/e297f9ee0f5984ed7d845886e21fdfd3cca72272/images/carbon%20budget%20consistent.png)
___
<br>


## Business-As-Usual and Net-Zero Scenario Construction

In this subsection, we expand in more detail on how we construct the NGFS current policy scenario and net zero scenario for annual emissions shown in *Figure 1*. The emission values on the y-axis of the left plots of *Figure 1* are obtained from Forward Analytics, except for total energy-related emissions. The total power sector emissions of coal, oil, and gas plants, respectively, are obtained by summing plant-level emissions of that type across all plants of that type in the world.


> **Note:**
> -  Plant-level emissions are given by the formula: annual CO₂ (in million tonnes) = capacity × capacity factor × heat rate (in Btu per kWh) × emission factor (kg of CO₂ per TJ) × \(9.2427 \times 10^{-12}\). 


Similarly, total extraction emissions of coal, oil, and gas mines/fields are obtained by summing mine/field-level emissions of that type across all mines/fields of that type in the world. For total energy emissions at the start of 2024 (black line in *Figure 1*), we take the 2023 energy-related emission estimate of 37.2 Gt CO₂ from the IEA. 


We use the plant and extraction-site specific emissions data (for each capturing Scope I and Scope II emissions) of Forward Analytics at \( t_0 = 2024 \) because the NGFS does not provide a granular breakdown of emissions beyond energy-related emissions and total emissions per country; these data are neither broken down by fuel type nor by plant/extraction site.


Taking the Forward Analytics emission data as a starting point, we then apply the NGFS projections under “current policies” (for the top left plot of Figure BAUNZScenarios) or “net-zero 2050” (for the bottom left plot of Figure *Figure 1*). As noted, the NGFS does not have projections at the country level broken down by fossil fuel type and sector (power/extraction), but it does have projections of primary energy outputs (extraction) and secondary energy outputs (power) in EJ broken down by country and fossil fuel type. Hence, we can convert these to emission projections and apply them (as rates of change) to our initial emissions (\( t_0 = 2024 \)) from Forward Analytics data.


For the projections of extraction emissions (primary energy), we use the conversion rates in *Table 3* to express NGFS projected EJ as projected extraction emissions E<sup>s<sub>NGFS</sub>, e<sub>extraction</sub></sup><sub>y,f,&tau;</sub> under scenario \( s \) (business as usual or net zero) for country \( y \) of fossil fuel extraction type \( f \) and time ( &tau; ).


___
**Table 3: Conversion of 1 EJ to CO₂ emissions**

| Fuel type | Conversion from 1 EJ                      | Conversion to CO₂                           |
|-----------|-------------------------------------------|---------------------------------------------|
| Coal      | 37.6 million ton coal equivalent          | 1764 kg CO₂ per ton                         |
| Oil       | 163.4 million barrels of oil equivalent   | 0.43 ton CO₂ per barrel                     |
| Gas       | 27.9 billion cubic meters                 | 1.9 kg CO₂ per cubic meter                  |
___


The conversion rates in the table above are obtained as follows:


- **Coal:** 1 EJ is converted to 34.12 million tonnes of coal equivalent according to the International Energy Agency's (IEA) converter, and then multiplied by a factor of 1.1 to convert to short tons (based on which the conversion to CO₂ is calculated), giving 37.6 million ton coal equivalent. The CO₂ coefficient is obtained from the Energy Information Administration.
- **Oil:** Conversion factors from BP's Statistical Review of World Energy are used to convert EJ to million barrels oil equivalent. Emissions factors are taken from the U.S. Environmental Protection Agency's (EPA) Greenhouse Gas Equivalencies Calculator.
- **Gas:** Similarly, conversion to cubic meters is performed using conversion factors from BP, and the CO₂ coefficients are obtained from the EIA.


To obtain the imputed NGFS projections of power sector emissions under the business as usual and net zero scenarios in *Figure 1*, we first use the factor 277,777,777 (or 277.8 TWh as reported by the IEA's conversion tool) to convert EJ to MWh. Next, we obtain the projected power sector emissions by multiplying the NGFS secondary energy projection 
S<sup>s<sub>level</sub>, e<sub>power</sub></sup><sub>y,f,&tau;</sub> (expressed in MWh) for scenario \( s \) (business as usual or net zero) in country \( y \) for fossil fuel \( f \) and time ( &tau; ) with the emission intensity I<sub>y,f</sub> for that country \( y \) and fossil fuel type \( f \):


<div align="center">
E<sup>s<sub>level</sub>, e<sub>power</sub></sup><sub>y,f,&tau;</sub> = I<sub>y,f</sub> &times; S<sup>s<sub>level</sub>, e<sub>power</sub></sup><sub>y,f,&tau;</sub>
</div>
<br>


where the superscript e<sub>power</sub> indicates these are power sector emissions. We obtain the emission intensity for country \( y \) and fuel type \( f \) as the weighted average (by activity in MWh) of the emission intensity of the power sector plants in that country and for that fuel type:


<div align="center">
I<sub>y,f</sub> = ( ∑<sub>l ∈ ℒ<sub>y,f</sub></sub> I<sub>y,f,l</sub> × A<sub>y,f,l</sub> ) / ( ∑<sub>l ∈ ℒ<sub>y,f</sub></sub> A<sub>y,f,l</sub> )
</div>
<br>


where I<sub>y,f,l</sub> is the emission intensity (in MtCO₂ per MWh) for power plant \( l \) in country \( y \) of fossil fuel type \( f \) from Forward Analytics data, A<sub>y,f,l</sub> is the activity (in MWh) for power plant \( l \) in country \( y \) of fossil fuel type \( f \) from Forward Analytics data, and \( \mathcal{L}_{y,f} \) is the set of power plants in country \( y \) of fossil fuel type \( f \).


Since we rely on our granular asset-level emission data for t<sub>0</sub>=2024 from Forward Analytics, we do not use the in-emissions-expressed NGFS projections for energy-related, extraction, and power-sector emissions in absolute levels (i.e., E<sup>s<sub>level</sub>, e<sub>energy-related</sub></sup><sub>y,&tau;</sub>, E<sup>s<sub>level</sub>, e<sub>extraction</sub></sup><sub>y,f,&tau;</sub>, E<sup>s<sub>level</sub>, e<sub>power</sub></sup><sub>y,f,&tau;</sub>, respectively), but rather as relative changes as follows (for t &isin; [t<sub>0</sub>+1, T]):


<div align="center">
E<sup>s,e</sup><sub>y,l,t</sub> =
</div>
<br>
<div align="center">
E<sup>e,data</sup><sub>y,l,t<sub>0</sub></sub> &times; ∏<sub>&tau; = t<sub>0</sub>+1</sub><sup>t</sup> ( 1 + ( E<sup>s<sub>level</sub>, e</sup><sub>y,&tau;</sub> - E<sup>s<sub>level</sub>, e</sup><sub>y,&tau;-1</sub> ) / E<sup>s<sub>level</sub>, e</sup><sub>y,&tau;-1</sub> ) = 
</div>
<br>
<div align="center">
E<sup>e,data</sup><sub>y,l,t<sub>0</sub></sub> &times; ∏<sub>&tau; = t<sub>0</sub>+1</sub><sup>t</sup> ( E<sup>s<sub>level</sub>, e</sup><sub>y,&tau;</sub> / E<sup>s<sub>level</sub>, e</sup><sub>y,&tau;-1</sub> )
</div>
<br>


We observe in the equation above that, given the initial emission data E<sup>e</sup><sub>y,l,t<sub>0</sub></sub> for energy in general (IEA, 37.2 Gt), extraction sites (Forward Analytics), and power plants (Forward Analytics) at the country level \( y \) and plant level \( l \) (where for energy-related emissions as a whole the subscript \( l \) does not apply), we can project emissions under the NGFS ( s = s<sub>1</sub> ) (business as usual) scenario or ( s = s<sub>2</sub> ) (net-zero 2050) scenario by multiplying iteratively with the relative difference of the NGFS emission projections at the absolute level:


<div align="center">
( E<sup>s<sub>level</sub>, e</sup><sub>y,&tau;</sub> / E<sup>s<sub>level</sub>, e</sup><sub>y,&tau;-1</sub> )
</div>
<br>


We note that the emission projections at the absolute level are country \( y \), fossil fuel type \( f \), and sector \( e \) specific, but not plant specific. Thus, all plants in a given country of a given fossil fuel type and sector (extraction/power) experience the same growth rates under ( s = s<sub>1</sub> ) (business as usual) and ( s = s<sub>2</sub> ) (net-zero 2050).

The annual emissions at each year t &isin; [t<sub>0</sub>+1, T] per fossil fuel and sector in Figure BAUNZScenarios are obtained by summing plant- or extraction-specific emissions E<sup>s,e</sup><sub>y,l,f,t</sub> across plants and countries, i.e.,


<div align="center">
E<sup>s,e</sup><sub>f,t</sub> = ∑<sub>y ∈ 𝒴</sub> ∑<sub>l ∈ ℒ<sub>y</sub></sub> E<sup>s,e</sup><sub>y,l,f,t</sub>.
</div>
<br>





[^1]: The numbers in brackets give the remaining carbon budget as of January 1, 2020, to limit global warming by 1.5/1.6/1.7/1.8/1.9/2 °C with 17%, 33%, 50%, 67%, 83% certainty (subject to variations and uncertainties quantified in IPCC 2021 Synthesis Report). The numbers without brackets give the remaining carbon budget left as of January 1, 2024, given 31.5 Gt energy-related CO₂ emissions in 2020, 36.1 Gt in 2021, 36.8 Gt in 2022, and 37.2 Gt in 2023, as per IEA estimates. For the 1.5 °C 50% NGFS decarbonization scenario we use the remaining carbon budget of \$358 Gt (shown in bold). The numbers without brackets do not capture non-energy-related CO₂ emissions and non-CO₂ GHG emissions. The remaining carbon budgets as of 2024 will thus in reality be more conservative than our estimates. (As of the beginning of 2025, the remaining carbon budget has also shrunk further. Our analysis, using carbon-budget aligned scenarios, enables us to easily redo the results based on the most recent carbon budget.)


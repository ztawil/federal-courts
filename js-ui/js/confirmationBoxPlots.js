
const width = 1600;
const height = 1000;
const margin = { top: 30, bottom: 50, left: 100, right: 60 };
const innerHeight = height - margin.bottom - margin.top;
const innerWidth = width - margin.left - margin.right;
const xValue = d => d.congress_start_year;
const yValue = d => d.days_to_confirm;
const radiusSize = 3;
const party = d => d.party_of_president;
const fullName = d => `${d.first_name} ${d.last_name}`;
const key = d => d.xValue;
const duration = 500;
const redColor = '#cc0808';
const blueColor = '#3440eb';
const getColorByRaw = partyString => partyString === 'Democratic' ? blueColor : redColor;
const getColor = d => getColorByRaw(party(d));
const getColorOfOpposition = partyOfPres => partyOfPres === 'Democratic' ? redColor : blueColor;
const circleShift = 50;
const boxWidth = 20;
const jitterWidth = innerWidth / 8;
const presidentPartySenateRatio = d => (.5 + (d.president_party_senate_majority_perc / 2))
const transitionDuration = 2000;
const backgroundOpacity = 0.2;

function getBoxPlotStats(dataArray) {
  const min = d3.min(dataArray);
  const max = d3.max(dataArray);
  const mean = d3.mean(dataArray);
  const median = d3.median(dataArray);
  const q1 = d3.quantileSorted(dataArray, .25);
  const q3 = d3.quantileSorted(dataArray, .75);
  const interQuartileRange = q3 - q1;
  const lowerFence = d3.max([min, q1 - (1.5 * interQuartileRange)]);
  const upperFence = d3.min([max, q3 + (1.5 * interQuartileRange)]);
  return { mean, median, q1, q3, interQuartileRange, min, max, lowerFence, upperFence };
}

const render = dataset => {

  const yearConfTimesSummaryStats = d3.rollup(dataset,
    v => {
      const daXValue = xValue(v[0])
      const party_of_president = party(v[0])
      const allAppointments = v
      const yearConfirmTimes = v
        .map(d => yValue(d))
        .sort(d3.ascending)
      const boxPlotStats = getBoxPlotStats(yearConfirmTimes)

      return { ...boxPlotStats, xValue: daXValue, party_of_president, allAppointments }
    },
    d => xValue(d)
  )

  function createSingleBoxPlot(innerG, datum, xScaleBand, xAxis, yScale, yAxis) {
    /*
    Create a single boxplot for a congressional year and bind the interactions on it
    datum is an object that has summary statistic for a given congress as well as a list of
    all appointments that happened in that year.
    */
    const boxplotGClass = "boxplotG";
    const allAppointments = datum.allAppointments;
    // Used to get some data for all appointments in this congress because data is duplicated

    // Create a group for this Congress' boxplot
    const boxPlotg = innerG.append("g")
      .attr('id', datum.xValue)
      .attr('transform', `translate(${xScaleBand(datum.xValue) + (boxWidth / 2) + 2}, 0)`)
      .classed(boxplotGClass, true);

    // Create verticle line
    boxPlotg.append('line')
      .attr("x1", 0)
      .attr("x2", 0)
      .attr("y1", yScale(datum.lowerFence))
      .attr("y2", yScale(datum.upperFence))
      .attr("stroke", "black")
      .attr("opacity", 1)
      .style("width", 40)
      .classed("vertLines", true);

    // Create the rectangle for the boxplot
    boxPlotg.append("rect")
      .attr("x", -boxWidth / 2)
      .attr("y", yScale(datum.q3))
      .attr("height", yScale(datum.q1) - yScale(datum.q3))
      .attr("width", boxWidth)
      .attr("stroke", "black")
      .attr("fill", getColor(datum))
      .attr("opacity", 1)
      .classed("boxes", true);

    // Add the median line
    boxPlotg.append("line")
      .attr("x1", -boxWidth / 2)
      .attr("x2", boxWidth / 2)
      .attr("y1", yScale(datum.median))
      .attr("y2", yScale(datum.median))
      .attr("stroke", "black")
      .style("width", 80)
      .attr("opacity", 1)
      .classed("medianLines", true);

    // Add an invisible bar ontop that is used to bind the click interactions.
    boxPlotg.append("rect")
      .attr("x", -boxWidth / 2)
      .attr("y", 0)
      .attr("height", innerHeight)
      .attr("width", boxWidth)
      .attr('fill', 'white')
      .attr('opacity', 0)
      .classed("invisibleBars", true)
      .on(
        // On click, all the other bars off the screen in a tranistion, then remove them.
        'click', function (_, d) {
          innerG
            .selectAll(`.${boxplotGClass}`)
            .filter(pointD => key(pointD) != key(datum))
            .transition()
            .duration(transitionDuration)
            .attr('transform', 'translate(-5000, 0)')
            .transition()
            .duration(transitionDuration)
            .remove();

          // Rescale the x Axis by the single congress
          xScaleBand.domain([datum.xValue]);
          xAxis.tickValues(xScaleBand.domain());
          innerG
            .select('.x.axis')
            .call(xAxis)
            .transition()
            .duration(transitionDuration);

          // Rescale the y Axis by all the appointments in this congress
          yScale.domain([0, d3.max(allAppointments, yValue)]);
          innerG
            .select('.y.axis')
            .call(yAxis)
            .transition()
            .duration(transitionDuration);

          // Move group to the middle of the screan
          boxPlotg
            .transition()
            .duration(transitionDuration)
            .attr('transform', `translate(${xScaleBand.bandwidth() / 2}, 0)`);

          // Lower the opacity and resize the boxplot elements given the new yScale
          boxPlotg.selectAll('.vertLines')
            .attr("opacity", backgroundOpacity)
            .attr("y1", yScale(datum.lowerFence))
            .attr("y2", yScale(datum.upperFence));

          boxPlotg.selectAll(".boxes")
            .attr("opacity", backgroundOpacity)
            .attr("y", yScale(datum.q3))
            .attr("height", yScale(datum.q1) - yScale(datum.q3));

          boxPlotg.selectAll(".medianLines")
            .attr("opacity", backgroundOpacity)
            .attr("y1", yScale(datum.median))
            .attr("y2", yScale(datum.median));

          const appendTexttoTG = (tG, appt) => {
            const textBlocks = [
              `Name: ${fullName(appt)}`,
              `Court: ${appt.court_name}`,
              `President: ${appt.president}`,
              `Senate Year: ${appt.congress_start_year}`,
              `% of Senate in Pres. Party: ${presidentPartySenateRatio(appt) * 100}`,
            ]
            textBlocks.forEach(tB => {
              tG
                .append('tspan')
                .attr('dy', '1em')
                .attr('x', innerWidth - 400)
                .text(tB);
            })
          }

          // Add circles for each of the individual appointments.
          // Add them around the boxplot using a random movement to the left and right.
          boxPlotg.selectAll('.nominationCircle')
            .data(allAppointments)
            .enter()
            .append('circle')
            .attr('cy', appt => yScale(yValue(appt)))
            .attr('cx', () => (-jitterWidth / 2) + (Math.random() * jitterWidth))
            .attr('r', 6)
            .attr('fill', getColor)
            .classed('nominationCircle', true)
            // On Mouseover show some details about the appointment
            .on('mouseover', (_, d) => {
              const tG = innerG
                .append('text')
                .attr('x', 0)
                .attr('y', margin.top)
                .classed('nominationCircleText', true);
              appendTexttoTG(tG, d);  // Add the texts
            })
            // Mousing out should remove the details
            .on('mouseout', () => innerG.selectAll('.nominationCircleText').remove());
          boxPlotg.selectAll('.invisibleBars').remove();
        })

    return boxPlotg.node();
  }

  function showAllBoxPlots() {
    // Create the band based on all years
    const xScaleBand = d3.scaleBand()
      .domain(congressYears)
      // It's going to be set inside the group that is already translated by the margin.
      .range([0, innerWidth]);

    const xAxis = d3
      .axisBottom(xScaleBand)
      .tickValues(xScaleBand.domain().filter(function (d) { return !(d % 5); }));  // Don't show all ticks
    xAxisG.call(xAxis);

    xAxisG.append('text')
      .classed("axis-label", true)
      .attr('x', innerWidth / 2)
      .attr('y', 40)
      .text("Congress of Judicial Nomination Year");

    const yScale = d3.scaleLinear()
      .domain([0, d3.max(nominationsByCongress, d => d.q3)])
      .range([innerHeight, 0]);

    const yAxis = d3.axisLeft(yScale);
    yAxisG.call(yAxis);

    yAxisG.append('text')
      .classed("axis-label", true)
      .text("Days to Confirmation")
      .attr('transform', 'rotate(270)')  // Rotate it to read vertically
      .attr('y', -60)
      .attr('x', -(innerHeight) / 2);

    // Create the box plot by congressional year
    innerG.selectAll(".boxplotG")
      .data(nominationsByCongress, key)
      .enter()
      // Need to pass in the x and y scales and Axes because they will be updated when a user clicks into a given bar
      .append(d => createSingleBoxPlot(innerG, d, xScaleBand, xAxis, yScale, yAxis));
  }

  const nominationsByCongress = [...yearConfTimesSummaryStats.values()].slice().sort((a, b) => d3.ascending(a.xValue, b.xValue))
  const congressYears = [...yearConfTimesSummaryStats.keys()].sort(d3.ascending)

  //Initial SVG
  const svg = d3.select('#visualization')
    .append('svg')
    .attr('width', width)
    .attr('height', height);

  // Create a group for the visualization
  const innerG = svg.append('g')
    .attr('transform', `translate(${margin.left}, ${margin.top})`)

  // Create a group for the x Axis labels. This needs to be globally scoped because it will update based on the user interaction
  const xAxisG = innerG.append('g')
    .attr('transform', `translate(0, ${innerHeight})`)
    .classed("x axis", true)

  // Create a group for the y Axis labels. This needs to be globally scoped because it will update based on the user interaction
  const yAxisG = innerG.append('g')
    .attr('transform', `translate(0, 0)`)
    .classed("y axis", true)

  // Initialize the graph with all the box plots showing
  showAllBoxPlots()
  svg.on('dblclick', () => {
    // Remove all the zoomed in annotations and show all boxplots again
    svg.selectAll('.boxplotG,.nominationCircleText').remove();
    showAllBoxPlots()
  })

}
d3.json('./joined_judges_wait.json').then(dataset => {
  render(dataset);
});

const renderEd = dataset => {
    const schoolCount = dataset[dataset.length-1].school_count_jd;
    console.log(schoolCount)

    const outerRadius = innerWidth / 4;
    const innerRadius = 0;

    const edSvg = d3.select('#education-visualization')
        .append('svg')
        .attr('height', height)
        .attr('width', width);

    innerEdG = edSvg.append('g')
        .attr('transform', `translate(${margin.left}, ${margin.top})`)

    const pie = d3.pie()
        .value(d => d.count)

    const arc = d3.arc()
        .innerRadius(innerRadius)
        .outerRadius(outerRadius);

    console.log(pie(schoolCount))
    const arcs = innerEdG.selectAll('g.arc')
        .data(pie(schoolCount))
        .enter()
        .append("g")
        .attr("class", "arc")
        .attr("transform", `translate(${outerRadius}, ${outerRadius})`)

    arcs.append('path')
        .attr('d', arc)
    
}

d3.json('./education_counts_by_year.json').then(dataset => {
    renderEd(dataset)
})
document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('file');
    const col1Select = document.getElementById('col1');
    const col2Select = document.getElementById('col2');
    const analyzeBtn = document.getElementById('analyze');
    const resultsDiv = document.getElementById('results');
    const loadingDiv = document.getElementById('loading');

    function showLoading() {
        loadingDiv.classList.remove('hidden');
        analyzeBtn.disabled = true;
    }

    function hideLoading() {
        loadingDiv.classList.add('hidden');
        analyzeBtn.disabled = false;
    }

    fileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        showLoading();
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (data.error) {
                alert(data.error);
                return;
            }

            // Populate column dropdowns
            const columns = data.columns;
            const options = columns.map(col => 
                `<option value="${col}">${col}</option>`
            ).join('');

            col1Select.innerHTML = '<option value="">Select column...</option>' + options;
            col2Select.innerHTML = '<option value="">Select column...</option>' + options;
            
            col1Select.disabled = false;
            col2Select.disabled = false;
            analyzeBtn.disabled = false;
        } catch (error) {
            alert('Error uploading file: ' + error);
        } finally {
            hideLoading();
        }
    });

    analyzeBtn.addEventListener('click', async () => {
        const col1 = col1Select.value;
        const col2 = col2Select.value;

        if (!col1 || !col2) {
            alert('Please select both columns');
            return;
        }

        showLoading();

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ col1, col2 })
            });

            const results = await response.json();
            
            if (results.error) {
                alert(results.error);
                return;
            }

            // Display results
            document.getElementById('recommendation').innerHTML = `
                <p class="font-semibold">Recommended Method: ${results.recommendation.method}</p>
                <p class="text-sm text-gray-600">Reason: ${results.recommendation.reason}</p>
                <p class="text-sm mt-2">Sample Size: ${results.metadata.sample_size}</p>
                <p class="text-sm">Total Ties: ${results.metadata.total_ties}</p>
            `;

            document.getElementById('kendall-results').innerHTML = `
                <p>Correlation: ${results.kendall.correlation.toFixed(3)}</p>
                <p>P-value: ${results.kendall.p_value.toFixed(3)}</p>
                <p>Interpretation: ${results.kendall.interpretation}</p>
            `;

            document.getElementById('spearman-results').innerHTML = `
                <p>Correlation: ${results.spearman.correlation.toFixed(3)}</p>
                <p>P-value: ${results.spearman.p_value.toFixed(3)}</p>
                <p>Interpretation: ${results.spearman.interpretation}</p>
            `;

            // Display visualizations
            const plotlyDiv = document.getElementById('plotly-div');
            const plotData = JSON.parse(results.visualizations);
            Plotly.newPlot(plotlyDiv, plotData.data, plotData.layout);

            resultsDiv.classList.remove('hidden');
        } catch (error) {
            alert('Error performing analysis: ' + error);
        } finally {
            hideLoading();
        }
    });
});
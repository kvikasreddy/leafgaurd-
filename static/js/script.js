document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('uploadForm');
  const status = document.getElementById('status');
  const resultBox = document.getElementById('resultBox');
  const predictionName = document.getElementById('predictionName');
  const predictionConfidence = document.getElementById('predictionConfidence');
  const predictionDescription = document.getElementById('predictionDescription');
  const predictionSolution = document.getElementById('predictionSolution');
  const historyList = document.getElementById('historyList');

  if (form) {
    form.addEventListener('submit', async (event) => {
      event.preventDefault();

      const fileInput = document.getElementById('leafImage');
      const file = fileInput.files[0];

      if (!file) {
        status.textContent = 'Please select an image first.';
        return;
      }

      status.textContent = 'Processing image...';

      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await fetch('/predict', {
          method: 'POST',
          body: formData,
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || 'Prediction failed');
        }

        status.textContent = 'Prediction complete.';
        resultBox.classList.remove('hidden');
        predictionName.textContent = data.prediction;
        predictionConfidence.textContent = `${data.confidence_percent}%`;
        predictionDescription.textContent = data.description || 'No description available.';
        predictionSolution.textContent = data.solution || 'No treatment advice available.';

        const currentResult = {
          disease: data.prediction,
          confidence: data.confidence_percent,
          description: data.description,
          solution: data.solution,
        };

        localStorage.setItem('leafguard_result', JSON.stringify(currentResult));
        updateResultSummary(currentResult);
      } catch (error) {
        status.textContent = error.message;
      }
    });
  }

  function updateResultSummary(result) {
    const resultDisease = document.getElementById('resultDisease');
    const resultConfidence = document.getElementById('resultConfidence');
    const resultDescription = document.getElementById('resultDescription');
    const resultSolution = document.getElementById('resultSolution');

    if (resultDisease) resultDisease.textContent = result.disease || 'Unknown';
    if (resultConfidence) resultConfidence.textContent = `${result.confidence || 0}%`;
    if (resultDescription) resultDescription.textContent = result.description || 'No description available.';
    if (resultSolution) resultSolution.textContent = result.solution || 'No treatment advice available.';
  }

  if (document.getElementById('resultDisease')) {
    const savedResult = JSON.parse(localStorage.getItem('leafguard_result') || '{}');
    if (savedResult.disease) {
      updateResultSummary(savedResult);
    }
  }

  if (historyList) {
    fetch('/api/history')
      .then((response) => response.json())
      .then((data) => {
        if (!data.history || data.history.length === 0) {
          historyList.innerHTML = '<p>No predictions yet.</p>';
          return;
        }

        historyList.innerHTML = data.history
          .map(
            (item) => `
              <div class="history-item">
                <p><strong>File:</strong> ${item.filename}</p>
                <p><strong>Disease:</strong> ${item.disease}</p>
                <p><strong>Confidence:</strong> ${(item.confidence * 100).toFixed(2)}%</p>
                <p><strong>Date:</strong> ${item.created_at}</p>
              </div>
            `
          )
          .join('');
      })
      .catch(() => {
        historyList.innerHTML = '<p>Unable to load history.</p>';
      });
  }
});

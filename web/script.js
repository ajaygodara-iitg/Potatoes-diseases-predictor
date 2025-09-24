const form = document.getElementById('uploadForm');
const fileInput = document.getElementById('fileInput');
const prediction = document.getElementById('prediction');
const confidence = document.getElementById('confidence');
const result = document.getElementById('result');
const uploadedImage = document.getElementById('uploadedImage');
const preview = document.getElementById('preview');
const farmerResponse = document.getElementById('farmerResponse');
const submitResponseBtn = document.getElementById('submitResponse');
const responseStatus = document.getElementById('responseStatus');
const analysisDiv = document.getElementById('perplexity');
const chatBox = document.getElementById('chatBox');

// Variables for flow
let diseaseName = "";
let previousAnswers = [];
let currentQuestion = "";
let currentQuestionCount = 0;
const maxQuestions = 10;

// Helper: Add message to chat
function addMessage(text, sender) {
    const msg = document.createElement('div');
    msg.classList.add('message', sender);
    msg.textContent = text;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Helper: Update counter
function updateCounter() {
    document.getElementById('questionCounter').textContent =
        `Question ${currentQuestionCount}/${maxQuestions}`;
}

// Show uploaded image preview
fileInput.addEventListener('change', () => {
    const file = fileInput.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            preview.src = e.target.result;
            uploadedImage.style.display = 'block';
        };
        reader.readAsDataURL(file);
    } else {
        uploadedImage.style.display = 'none';
    }
});

// Handle predict
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const file = fileInput.files[0];
    if (!file) return alert('Please upload an image file.');

    const formData = new FormData();
    formData.append('file', file);

    prediction.textContent = 'Processing...';
    confidence.textContent = '';
    analysisDiv.innerHTML = '';
    chatBox.innerHTML = '';  // Clear chat
    result.style.display = 'block';

    try {
        const response = await fetch('http://localhost:8080/predict', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) throw new Error('Prediction failed');

        const data = await response.json();

        prediction.textContent = `Class: ${data.class}`;
        confidence.textContent = `Confidence: ${(data.confidence * 100).toFixed(2)}%`;
        analysisDiv.innerHTML = data.analysis_html;

        // Reset state
        diseaseName = data.class;
        previousAnswers = [];
        currentQuestionCount = 0;
        updateCounter();

        // Fetch first question
        await fetchNextQuestion();

    } catch (error) {
        prediction.textContent = 'Error: Unable to process the image.';
        confidence.textContent = '';
    }
});

// Fetch next follow-up question
async function fetchNextQuestion() {
    if (currentQuestionCount >= maxQuestions) {
        addMessage("You have reached the maximum number of questions.", "ai");
        await fetchSummary();
        return;
    }

    const payload = {
        disease_name: diseaseName,
        previous_answers: previousAnswers
    };

    try {
        const response = await fetch('http://localhost:8080/next-question', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error('Failed to fetch next question');
        const data = await response.json();

        currentQuestion = data.question;

        // Check if Gemini signals no more questions
        if (!currentQuestion || currentQuestion.toLowerCase().includes('no further')) {
            addMessage("No further questions.", "ai");
            await fetchSummary();
            return;
        }

        currentQuestionCount++;
        updateCounter();
        addMessage(currentQuestion, "ai");

    } catch (err) {
        addMessage("Could not fetch next question.", "ai");
    }
}

// Fetch summary/recommendations
async function fetchSummary() {
    const payload = {
        disease_name: diseaseName,
        previous_answers: previousAnswers
    };

    try {
        const response = await fetch('http://localhost:8080/summary', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error('Failed to fetch summary');
        const data = await response.json();

        // Show recommendations in chat
        addMessage("Summary & Recommendations:", "ai");
        const summaryDiv = document.createElement('div');
        summaryDiv.classList.add('message', 'ai');
        summaryDiv.innerHTML = data.summary_html;
        chatBox.appendChild(summaryDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    } catch (err) {
        addMessage("Could not generate summary.", "ai");
    }
}

// Submit farmer response
submitResponseBtn.addEventListener('click', async () => {
    const responseText = farmerResponse.value.trim();
    if (!responseText) return alert('Please type your answer.');

    // Show farmer answer in chat
    addMessage(responseText, "farmer");

    // Save answer for context
    previousAnswers.push(`${currentQuestion} -> ${responseText}`);

    // Save response to backend
    const formData = new FormData();
    formData.append('response_text', responseText);
    formData.append('disease_name', diseaseName);
    formData.append('question_text', currentQuestion);

    try {
        await fetch('http://localhost:8080/farmer-response', {
            method: 'POST',
            body: formData,
        });

        // Fetch next question
        await fetchNextQuestion();

    } catch (err) {
        responseStatus.textContent = 'Error saving response.';
    }

    farmerResponse.value = ''; // clear input
});

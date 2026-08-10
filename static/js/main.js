let chartInstance = null;


/* =========================================
   INITIALIZE
========================================= */

document.addEventListener("DOMContentLoaded", () => {
    loadUsers();
    loadAnalyticsChart();
});


/* =========================================
   LOAD USERS
========================================= */

async function loadUsers() {

    const select = document.getElementById("userSelect");

    try {

        const response = await fetch("/api/users");

        if (!response.ok) {
            throw new Error("Unable to load readers");
        }

        const data = await response.json();

        select.innerHTML = "";

        data.users.forEach(user => {

            const option = document.createElement("option");

            option.value = user;
            option.textContent = user;

            select.appendChild(option);

        });

        const readerCount = document.getElementById("readerCount");

        if (readerCount) {
            readerCount.textContent = data.users.length;
        }

    } catch (error) {

        console.error("User loading error:", error);

        select.innerHTML =
            "<option>Unable to load readers</option>";
    }
}


/* =========================================
   GET RECOMMENDATIONS
========================================= */

async function getRecommendations() {

    const user =
        document.getElementById("userSelect").value;

    const metric =
        document.getElementById("metricSelect").value;

    const button =
        document.getElementById("recommendButton");


    if (!user || user.includes("Unable")) {
        return;
    }


    /* Loading state */

    button.classList.add("loading");

    button.innerHTML = `
        <span>✨</span>
        Finding your reading match...
    `;


    try {

        const response = await fetch("/api/recommend", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                user: user,
                metric: metric
            })

        });


        if (!response.ok) {

            let errorMessage = "Recommendation failed";

            try {

                const errorData =
                    await response.json();

                errorMessage =
                    errorData.detail || errorMessage;

            } catch (error) {
                // Keep default error message
            }

            throw new Error(errorMessage);
        }


        const data =
            await response.json();

        renderResults(data);


    } catch (error) {

        console.error("Recommendation error:", error);

        showError(error.message);

    } finally {

        button.classList.remove("loading");

        button.innerHTML = `
            <span>✨</span>
            Find My Recommendations
            <span>→</span>
        `;

    }

}


/* =========================================
   RENDER RESULTS
========================================= */

function renderResults(data) {

    const resultsSection =
        document.getElementById("resultsSection");

    const targetUser =
        document.getElementById("targetUser");

    const similarUser =
        document.getElementById("similarUser");

    const similarityScore =
        document.getElementById("similarityScore");

    const similarityLabel =
        document.getElementById("similarityLabel");

    const infoSimilarUser =
        document.getElementById("infoSimilarUser");

    const infoBookCount =
        document.getElementById("infoBookCount");

    const description =
        document.getElementById("matchDescription");

    const list =
        document.getElementById("recommendationsList");


    /* -----------------------------------------
       SHOW RESULTS
    ----------------------------------------- */

    resultsSection.classList.remove("hidden");


    /* -----------------------------------------
       USER INFORMATION
    ----------------------------------------- */

    if (targetUser) {
        targetUser.textContent =
            data.target_user;
    }

    if (similarUser) {
        similarUser.textContent =
            data.most_similar_user;
    }


    /* -----------------------------------------
       SIMILARITY / DISTANCE SCORE
    ----------------------------------------- */

    let displayScore;


    if (data.metric_used === "cosine") {

        if (similarityLabel) {
            similarityLabel.textContent =
                "COSINE SIMILARITY";
        }

        displayScore =
            `${(Number(data.score) * 100).toFixed(1)}%`;


        if (description) {

            description.textContent =
                `Your reading preferences have a ${displayScore} similarity with ${data.most_similar_user}. Books rated highly by this reader are used to generate your recommendations.`;

        }

    } else {

        if (similarityLabel) {
            similarityLabel.textContent =
                "EUCLIDEAN DISTANCE";
        }

        displayScore =
            Number(data.score).toFixed(2);


        if (description) {

            description.textContent =
                `BookWise found ${data.most_similar_user} as your closest reader using Euclidean distance. A smaller distance means the two reading vectors are more similar.`;

        }

    }


    if (similarityScore) {
        similarityScore.textContent =
            displayScore;
    }


    /* -----------------------------------------
       EXTRA RESULT INFORMATION
    ----------------------------------------- */

    if (infoSimilarUser) {

        infoSimilarUser.textContent =
            data.most_similar_user;

    }


    if (infoBookCount) {

        infoBookCount.textContent =
            data.recommendations
                ? data.recommendations.length
                : 0;

    }


    /* -----------------------------------------
       RECOMMENDATION CARDS
    ----------------------------------------- */

    list.innerHTML = "";


    if (
        !data.recommendations ||
        data.recommendations.length === 0
    ) {

        list.innerHTML = `

            <div class="no-results">

                <h3>
                    No recommendations yet
                </h3>

                <p>
                    We couldn't find books that meet
                    the recommendation criteria for
                    this reader.
                </p>

            </div>

        `;

    } else {

        data.recommendations.forEach(
            (item, index) => {

                const card =
                    createBookCard(
                        item,
                        data.most_similar_user,
                        index
                    );

                list.appendChild(card);

            }
        );

    }


    /* -----------------------------------------
       SCROLL TO RESULTS
    ----------------------------------------- */

    setTimeout(() => {

        resultsSection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    }, 100);

}


/* =========================================
   CREATE BOOK CARD
========================================= */


function createBookCard(item, similarUser, index) {

    const card = document.createElement("div");
    card.className = "book-card";

    /* -----------------------------------------
       BOOK TITLE
    ----------------------------------------- */

    const title = item.book
        .replace(/_/g, " ")
        .replace(/\s+/g, " ")
        .trim();

    /* -----------------------------------------
       RATINGS
    ----------------------------------------- */

    const similarRating =
        Number(item.similar_user_rating).toFixed(1);

    const targetRating =
        Number(item.target_user_rating).toFixed(1);

    const difference =
        item.rating_difference !== undefined
            ? Number(item.rating_difference).toFixed(1)
            : (
                Number(item.similar_user_rating) -
                Number(item.target_user_rating)
            ).toFixed(1);

    /* -----------------------------------------
       BOOK COVER STYLES
    ----------------------------------------- */

    const coverStyles = [
        "linear-gradient(145deg, #6657f5, #9a8cff)",
        "linear-gradient(145deg, #3f8cff, #78b8ff)",
        "linear-gradient(145deg, #e36b8a, #f0a2b4)",
        "linear-gradient(145deg, #4a9c83, #78c9ad)",
        "linear-gradient(145deg, #e99b43, #f4c37e)"
    ];

    const coverStyle =
        coverStyles[index % coverStyles.length];

    /* -----------------------------------------
       BOOK CARD
    ----------------------------------------- */

    card.innerHTML = `
        <div
            class="book-cover"
            style="background: ${coverStyle}"
        >
            <div class="cover-title">
                ${escapeHTML(title)}
            </div>
        </div>

        <div class="book-info">

            <h4>
                ${escapeHTML(title)}
            </h4>

            <div class="book-rating">

                <span class="star">
                    ★
                </span>

                <span class="rating-number">
                    ${similarRating}/5
                </span>

                <span>
                    Similar reader's rating
                </span>

            </div>

            <div class="book-source">
                You rated this ${targetRating}/5
            </div>

            <div class="book-source">
                Your closest match rated it
                ${difference} point${difference == 1 ? "" : "s"} higher.
            </div>

            <span class="recommended-badge">
                Recommended for you
            </span>

        </div>
    `;

    return card;
}


/* =========================================
   ESCAPE HTML
========================================= */

function escapeHTML(value) {
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

        
/* =========================================
   BACK TO FINDER
========================================= */

function backToFinder() {

    const finder =
        document.getElementById("finder");

    if (!finder) {
        return;
    }

    finder.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });

}


/* =========================================
   ERROR MESSAGE
========================================= */

function showError(message) {

    const resultsSection =
        document.getElementById("resultsSection");

    const recommendationsList =
        document.getElementById(
            "recommendationsList"
        );


    resultsSection.classList.remove("hidden");


    recommendationsList.innerHTML = `

        <div class="no-results">

            <h3>
                We couldn't find your recommendations.
            </h3>

            <p>
                ${escapeHTML(
                    message ||
                    "Something went wrong. Please try again."
                )}
            </p>

        </div>

    `;


    resultsSection.scrollIntoView({
        behavior: "smooth"
    });

}


/* =========================================
   ANALYTICS
========================================= */

async function loadAnalyticsChart() {

    try {

        const response =
            await fetch("/api/analytics");


        if (!response.ok) {
            throw new Error(
                "Analytics unavailable"
            );
        }


        const data =
            await response.json();


        /* -----------------------------------------
           FORMAT BOOK NAMES
        ----------------------------------------- */

        const books =
            data.books.map(
                book =>
                    book
                        .replace(/_/g, " ")
                        .replace(/\s+/g, " ")
                        .trim()
            );


        /* -----------------------------------------
           CONVERT RATINGS TO NUMBERS
        ----------------------------------------- */

        const ratings =
            data.average_ratings.map(Number);


        /* -----------------------------------------
           DATASET STATISTICS
        ----------------------------------------- */

        const bookCount =
            document.getElementById(
                "bookCount"
            );

        if (bookCount) {
            bookCount.textContent =
                books.length;
        }


        if (ratings.length > 0) {

            const average =
                ratings.reduce(
                    (sum, value) =>
                        sum + value,
                    0
                ) / ratings.length;


            const averageRating =
                document.getElementById(
                    "averageRating"
                );

            if (averageRating) {

                averageRating.textContent =
                    average.toFixed(1);

            }


            const highestIndex =
                ratings.indexOf(
                    Math.max(...ratings)
                );


            const topBook =
                document.getElementById(
                    "topBook"
                );

            if (topBook) {

                topBook.textContent =
                    books[highestIndex];

            }

        }


        /* -----------------------------------------
           CHART
        ----------------------------------------- */

        const canvas =
            document.getElementById(
                "averageChart"
            );


        if (!canvas) {
            return;
        }


        if (chartInstance) {
            chartInstance.destroy();
        }


        chartInstance =
            new Chart(
                canvas,
                {

                    type: "bar",


                    data: {

                        labels: books,

                        datasets: [

                            {

                                label:
                                    "Average rating",

                                data:
                                    ratings,

                                backgroundColor:
                                    "rgba(103, 87, 245, 0.72)",

                                borderColor:
                                    "#6757f5",

                                borderWidth: 1,

                                borderRadius: 8

                            }

                        ]

                    },


                    options: {

                        responsive: true,

                        maintainAspectRatio: false,


                        plugins: {

                            legend: {
                                display: false
                            },


                            tooltip: {

                                callbacks: {

                                    label:
                                        context =>
                                            ` Average rating: ${context.parsed.y.toFixed(1)}/5`

                                }

                            }

                        },


                        scales: {

                            y: {

                                beginAtZero: true,

                                max: 5,

                                ticks: {
                                    stepSize: 1
                                },

                                title: {

                                    display: true,

                                    text:
                                        "Average rating (1–5)"

                                }

                            },


                            x: {

                                ticks: {

                                    maxRotation: 45,

                                    minRotation: 35

                                }

                            }

                        }

                    }

                }
            );


    } catch (error) {

        console.error(
            "Analytics error:",
            error
        );

    }

}
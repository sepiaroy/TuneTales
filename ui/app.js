const image_container = document.getElementById('image-container');
const search_bar = document.querySelector('.search-bar');
const book_name = document.getElementById('book-name');
const author_name = document.getElementById('author-name');
const search_button = document.getElementById('search-button');
const search_warning = document.querySelector('.search-warning');
const song_results = document.getElementById('song-results');
const spinner = document.querySelector('.spinner');
const song_error = document.getElementById('song-error');

search_button.addEventListener('click', () => {
    song_error.style.display = "none";
    song_results.innerHTML = '';
    const bookName = book_name.value;
    const authorName = author_name.value;

    if (bookName === "" || authorName === "") {
        search_warning.style.display = "block";
    } else {
        search_warning.style.display = "none";

        spinner.style.display = "block";
        fetch('http://localhost:5000/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                bookTitle: bookName,
                bookAuthor: authorName
            })
        })
        .then(res => res.json())
        .then(data => {
            spinner.style.display = "none";
            if (data.error) {
                console.error(data.error);
                displayError();
            } else {
                const songs = data.songs;
                // console.log(songs)
                spinner.style.display = "none";
                displaySongs(songs);  
            }
        })
        .catch(err => {
            spinner.style.display = "none";
            console.error("Failed:", err);
            displayError();
        });
    }
})

function displaySongs(songs) {
    search_bar.style.display = "none";
    image_container.style.display = "none";
    const rec_songs = document.createElement('p');
    rec_songs.className = 'rec-songs';
    rec_songs.textContent = "Top Recommended Songs:";
    song_results.appendChild(rec_songs);

    songs.forEach(song => {
        const songElement = document.createElement('div');
        songElement.className = 'song-embed';
    
        const embedUrl = `https://open.spotify.com/embed/track/${song.id}`;

        songElement.innerHTML = `
            <iframe style="border-radius:12px"
                src="${embedUrl}?utm_source=generator"
                width="100%" height="80" frameBorder="0" allowfullscreen=""
                allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                loading="lazy"></iframe>
        `;

        song_results.appendChild(songElement);
    });

    const back_button = document.createElement('button');
    back_button.textContent = "Back";
    back_button.style.width = "55px";
    back_button.style.height = "40px";

    song_results.appendChild(back_button);

    song_results.style.display = "flex";

    back_button.addEventListener('click', ()=> {
        song_results.style.display = "none";
        search_bar.style.display = "flex";
        image_container.style.display = "block";
    });
}

function displayError() {
    song_error.style.display = "block";
}




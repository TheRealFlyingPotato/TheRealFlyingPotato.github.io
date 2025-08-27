$(document).ready(function() {
    // Load board games data from JSON file
    loadBoardGames();
    
    // Set up real-time filtering
    setupFilters();
    
    // Load URL parameters and apply filters if they exist
    loadUrlParameters();
    
    // Set up print functionality
    setupPrint();
});

function setupPrint() {
    // Create print table when page loads
    window.addEventListener('beforeprint', createPrintTable);
}

function createPrintTable() {
    // Remove existing print table
    $('.print-table').remove();
    
    // Get all visible games
    const visibleGames = [];
    $('.game-card:visible').each(function() {
        const gameData = {
            image: $(this).find('img').attr('src') || '',
            name: $(this).find('.card-title').text(),
            genre: $(this).find('.badge.bg-secondary').text(),
            players: $(this).find('.badge.bg-primary').text(),
            weight: $(this).find('.badge.bg-info').text(),
            description: $(this).data('description') || ''
        };
        visibleGames.push(gameData);
    });
    
    // Create table HTML
    let tableHtml = `
        <table class="print-table">
            <thead>
                <tr>
                    <th class="col-image">Image</th>
                    <th class="col-name">Name</th>
                    <th class="col-genre">Genre</th>
                    <th class="col-players">Players</th>
                    <th class="col-weight">Weight</th>
                    <th class="col-description">Description</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    visibleGames.forEach(game => {
        tableHtml += `
            <tr>
                <td class="col-image"><img src="${game.image}" alt="${game.name}"></td>
                <td class="col-name">${game.name}</td>
                <td class="col-genre">${game.genre}</td>
                <td class="col-players">${game.players}</td>
                <td class="col-weight">${game.weight}</td>
                <td class="col-description">${game.description}</td>
            </tr>
        `;
    });
    
    tableHtml += `
            </tbody>
        </table>
    `;
    
    // Add table to page
    $('.boardgames').after(tableHtml);
}

function loadUrlParameters() {
    const urlParams = new URLSearchParams(window.location.search);
    const ids = urlParams.get('ids');
    
    if (ids) {
        $('#idFilter').val(ids);
        // Apply filters after a short delay to ensure games are loaded
        setTimeout(() => {
            applyFilters();
        }, 100);
    }
}

function toggleGameIdInUrl(gameId) {
    const url = new URL(window.location);
    const currentIds = url.searchParams.get('ids');
    let idList = currentIds ? currentIds.split(',').map(id => id.trim()) : [];
    
    const gameIdStr = gameId.toString();
    
    if (idList.includes(gameIdStr)) {
        // Remove ID
        idList = idList.filter(id => id !== gameIdStr);
    } else {
        // Add ID
        idList.push(gameIdStr);
    }
    
    // Update URL parameters
    if (idList.length > 0) {
        url.searchParams.set('ids', idList.join(','));
    } else {
        url.searchParams.delete('ids');
    }
    
    // Update URL without reloading the page
    window.history.pushState({}, '', url);
}

function updateUrlParameters() {
    const idFilter = $('#idFilter').val().trim();
    const url = new URL(window.location);
    
    if (idFilter) {
        url.searchParams.set('ids', idFilter);
    } else {
        url.searchParams.delete('ids');
    }
    
    // Update URL without reloading the page
    window.history.pushState({}, '', url);
}

function setupFilters() {
    // Add event listeners to all filter inputs for real-time filtering
    $('#nameFilter, #playerCountFilter, #genreFilter, #weightFilter, #idFilter').on('input', function() {
        applyFilters();
        
        // Update URL parameters when ID filter changes
        if ($(this).attr('id') === 'idFilter') {
            updateUrlParameters();
        }
    });
}

function applyFilters() {
    const filters = {
        name: $('#nameFilter').val().trim(),
        playerCount: $('#playerCountFilter').val().trim(),
        genre: $('#genreFilter').val().trim(),
        weight: $('#weightFilter').val().trim(),
        id: $('#idFilter').val().trim()
    };
    
    $('.game-card').each(function() {
        const card = $(this);
        const gameData = {
            name: card.data('name') || '',
            playerCount: card.data('player-count') || '',
            genre: card.data('genre') || '',
            weight: card.data('weight') || '',
            id: card.data('id') || '',
            description: card.data('description') || '',
            notes: card.data('notes') || ''
        };
        
        let showCard = true;
        
        // Apply each filter
        if (filters.name && !matchesTextFilter(filters.name, gameData.name + ' ' + gameData.description + ' ' + gameData.notes)) {
            showCard = false;
        }
        
        if (filters.playerCount && !matchesPlayerCountFilter(filters.playerCount, gameData.playerCount)) {
            showCard = false;
        }
        
        if (filters.genre && !matchesTextFilter(filters.genre, gameData.genre)) {
            showCard = false;
        }
        
        if (filters.weight && !matchesWeightFilter(filters.weight, gameData.weight)) {
            showCard = false;
        }
        
        if (filters.id && !matchesIdFilter(filters.id, gameData.id)) {
            showCard = false;
        }
        
        // Show/hide card with smooth animation
        if (showCard) {
            card.show();
        } else {
            card.hide();
        }
    });
}

function matchesTextFilter(filterValue, gameText) {
    const lowerFilter = filterValue.toLowerCase();
    const lowerGameText = gameText.toLowerCase();
    
    // Handle AND operator (&)
    if (lowerFilter.includes('&')) {
        const andTerms = lowerFilter.split('&').map(term => term.trim());
        return andTerms.every(term => lowerGameText.includes(term));
    }
    
    // Handle OR operator (,)
    if (lowerFilter.includes(',')) {
        const orTerms = lowerFilter.split(',').map(term => term.trim());
        return orTerms.some(term => lowerGameText.includes(term));
    }
    
    // Simple contains match
    return lowerGameText.includes(lowerFilter);
}

function matchesPlayerCountFilter(filterValue, gamePlayerCount) {
    // Handle exact match with = prefix
    if (filterValue.startsWith('=')) {
        const exactNum = parseInt(filterValue.substring(1));
        if (!isNaN(exactNum)) {
            return gamePlayerCount.toString() === exactNum.toString();
        }
    }
    
    const processedFilter = processNumericFilter(filterValue);
    const gamePlayerNumbers = parsePlayerCount(gamePlayerCount);
    
    // Handle AND operator (&)
    if (filterValue.includes('&')) {
        const andTerms = filterValue.split('&').map(term => term.trim());
        return andTerms.every(term => {
            if (term.startsWith('=')) {
                const exactNum = parseInt(term.substring(1));
                return gamePlayerCount.toString() === exactNum.toString();
            }
            const termNumbers = processNumericFilter(term);
            return termNumbers.some(filterNum => 
                gamePlayerNumbers.some(gameNum => gameNum === filterNum)
            );
        });
    }
    
    // Handle OR operator (,) or simple match
    return processedFilter.some(filterNum => 
        gamePlayerNumbers.some(gameNum => gameNum === filterNum)
    );
}

function matchesWeightFilter(filterValue, gameWeight) {
    const processedFilter = processNumericFilter(filterValue);
    const gameWeightNum = parseInt(gameWeight);
    
    // Handle AND operator (&)
    if (filterValue.includes('&')) {
        const andTerms = filterValue.split('&').map(term => term.trim());
        return andTerms.every(term => {
            const termNumbers = processNumericFilter(term);
            return termNumbers.includes(gameWeightNum);
        });
    }
    
    // Handle OR operator (,) or simple match
    return processedFilter.includes(gameWeightNum);
}

function matchesIdFilter(filterValue, gameId) {
    const gameIdNum = parseInt(gameId);
    
    // Handle AND operator (&) - all IDs must match (doesn't make sense for IDs but kept for consistency)
    if (filterValue.includes('&')) {
        const andTerms = filterValue.split('&').map(term => parseInt(term.trim())).filter(num => !isNaN(num));
        return andTerms.every(term => term === gameIdNum);
    }
    
    // Handle OR operator (,) - any ID can match
    if (filterValue.includes(',')) {
        const orTerms = filterValue.split(',').map(term => parseInt(term.trim())).filter(num => !isNaN(num));
        return orTerms.includes(gameIdNum);
    }
    
    // Simple exact match
    const filterNum = parseInt(filterValue);
    return !isNaN(filterNum) && filterNum === gameIdNum;
}

function processNumericFilter(filterValue) {
    let numbers = [];
    
    // Split by OR operator first
    const orTerms = filterValue.split(',').map(term => term.trim());
    
    orTerms.forEach(term => {
        if (term.includes('-')) {
            // Handle range (e.g., "1-3" becomes [1,2,3])
            const [start, end] = term.split('-').map(num => parseInt(num.trim()));
            if (!isNaN(start) && !isNaN(end)) {
                for (let i = start; i <= end; i++) {
                    numbers.push(i);
                }
            }
        } else {
            // Handle single number
            const num = parseInt(term);
            if (!isNaN(num)) {
                numbers.push(num);
            }
        }
    });
    
    // Remove duplicates
    return [...new Set(numbers)];
}

function parsePlayerCount(playerCountString) {
    const str = playerCountString.toString().toLowerCase();
    let numbers = [];
    
    if (str.includes('-')) {
        // Handle range like "2-4" or "2-5"
        const parts = str.split('-');
        if (parts.length === 2) {
            const start = parseInt(parts[0]);
            const end = parseInt(parts[1].replace(/[^\d]/g, '')); // Remove non-digits
            
            if (!isNaN(start) && !isNaN(end)) {
                for (let i = start; i <= end; i++) {
                    numbers.push(i);
                }
            }
        }
    } else if (str.includes('+')) {
        // Handle "4+" - assume up to reasonable max (8)
        const baseNum = parseInt(str.replace('+', ''));
        if (!isNaN(baseNum)) {
            for (let i = baseNum; i <= 8; i++) {
                numbers.push(i);
            }
        }
    } else {
        // Try to extract number
        const match = str.match(/\d+/);
        if (match) {
            numbers.push(parseInt(match[0]));
        }
    }
    
    return numbers;
}

function loadBoardGames() {
    // Try to load local JSON file first
    $.getJSON('boardgames.json')
        .done(function(data) {
            displayBoardGames(data);
        })
        .fail(function(jqxhr, textStatus, error) {
            console.warn('Local boardgames.json failed, trying GitHub fallback:', textStatus, error);
            
            // Fallback to GitHub raw JSON file
            const githubUrl = 'https://raw.githubusercontent.com/username/boardgames-data/main/boardgames.json';
            
            $.ajax({
                url: githubUrl,
                method: 'GET',
                dataType: 'json',
                timeout: 10000, // 10 second timeout
                success: function(data) {
                    console.log('Successfully loaded from GitHub fallback');
                    displayBoardGames(data);
                },
                error: function(xhr, status, errorThrown) {
                    console.error('GitHub fallback also failed:', status, errorThrown);
                    displayErrorMessage();
                }
            });
        });
}

function displayBoardGames(games) {
    const container = $('.boardgames .row');
    
    // Clear existing content
    container.empty();
    
    // Create game cards
    games.forEach(function(game) {
        const gameCard = createGameCard(game);
        container.append(gameCard);
    });
}

function createGameCard(game) {
    // Create responsive column
    const col = $('<div>', {
        class: 'col-12 col-md-6 col-lg-4 mb-4 game-card',
        'data-id': game.id,
        'data-name': game.name.toLowerCase(),
        'data-genre': game.genre.toLowerCase(),
        'data-description': game.description.toLowerCase(),
        'data-player-count': game['player count'],
        'data-notes': game.notes ? game.notes.toLowerCase() : '',
        'data-weight': game.weight
    });
    
    // Create card
    const card = $('<div>', {
        class: 'card h-100 shadow-sm position-relative',
        style: 'cursor: pointer; transition: transform 0.3s ease, box-shadow 0.3s ease;'
    });
    
    // Add colored top border if color is provided
    if (game.color) {
        card.css('border-top', `4px solid ${game.color}`);
    }
    
    // Create image container
    const imgContainer = $('<div>', {
        class: 'card-img-top-container position-relative overflow-hidden',
        style: 'height: 200px;'
    });
    
    // Create image
    const img = $('<img>', {
        src: game.image,
        alt: game.name,
        class: 'card-img-top w-100 h-100',
        style: 'object-fit: cover;',
        loading: 'lazy'
    });
    
    // Create overlay for description/notes (initially hidden)
    const overlay = $('<div>', {
        class: 'position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center p-3',
        style: 'background-color: rgba(0, 0, 0, 0.25); opacity: 0; transition: opacity 0.3s ease; z-index: 10;'
    });
    
    const overlayContent = $('<div>', {
        class: 'text-white text-center'
    });
    
    // Add description to overlay
    const overlayDescription = $('<p>', {
        class: 'mb-2 small fw-bold text-shadow',
        text: game.description,
        style: 'text-shadow: 1px 1px 2px rgba(0,0,0,0.8);'
    });
    
    // Add notes to overlay if they exist
    let overlayNotes = null;
    if (game.notes && game.notes.trim() !== '') {
        overlayNotes = $('<p>', {
            class: 'mb-0 small text-warning fw-bold',
            html: `<strong>Notes:</strong> ${game.notes}`,
            style: 'text-shadow: 1px 1px 2px rgba(0,0,0,0.8);'
        });
    }
    
    overlayContent.append(overlayDescription);
    if (overlayNotes) {
        overlayContent.append(overlayNotes);
    }
    overlay.append(overlayContent);
    
    // Add hover events for desktop
    card.hover(
        function() { 
            $(this).css({
                'transform': 'scale(1.03)',
                'box-shadow': '0 8px 25px rgba(0,0,0,0.15)'
            });
            $(this).find('.overlay').css('opacity', '1');
        },
        function() { 
            $(this).css({
                'transform': 'scale(1)',
                'box-shadow': ''
            });
            $(this).find('.overlay').css('opacity', '0');
        }
    );
    
    // Click for mobile overlay AND ID management
    card.click(function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const currentOverlay = $(this).find('.overlay');
        const isVisible = currentOverlay.css('opacity') == '1';
        
        // Toggle overlay (for mobile)
        if (isVisible) {
            $(this).css({
                'transform': 'scale(1)',
                'box-shadow': ''
            });
            currentOverlay.css('opacity', '0');
        } else {
            $(this).css({
                'transform': 'scale(1.03)',
                'box-shadow': '0 8px 25px rgba(0,0,0,0.15)'
            });
            currentOverlay.css('opacity', '1');
        }
        
        // Always toggle ID in URL
        toggleGameIdInUrl(game.id);
    });
    
    overlay.addClass('overlay');
    imgContainer.append(img, overlay);
    
    // Create card body
    const cardBody = $('<div>', {
        class: 'card-body d-flex flex-column'
    });
    
    // Game title
    const title = $('<h5>', {
        class: 'card-title mb-2',
        text: game.name
    });
    
    // Badges container
    const badgesContainer = $('<div>', {
        class: 'mb-2'
    });
    
    // Genre badge
    const genreBadge = $('<span>', {
        class: 'badge bg-secondary me-2 mb-1',
        text: game.genre
    });
    
    // Player count badge
    const playerBadge = $('<span>', {
        class: 'badge bg-primary me-2 mb-1',
        text: `${game['player count']} players`
    });
    
    // Weight badge
    const weightBadge = $('<span>', {
        class: 'badge bg-info mb-1',
        text: `Weight: ${game.weight}/5`
    });
    
    badgesContainer.append(genreBadge, playerBadge, weightBadge);
    
    // More info indicator with magnifying glass icon
    const moreInfoIndicator = $('<div>', {
        class: 'mt-auto text-center text-muted',
        style: 'font-size: 1.2rem;'
    }).append(
        $('<svg>', {
            xmlns: 'http://www.w3.org/2000/svg',
            width: '16',
            height: '16',
            fill: 'currentColor',
            class: 'bi bi-search',
            viewBox: '0 0 16 16',
            style: 'opacity: 0.6;'
        }).append(
            $('<path>', {
                d: 'M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z'
            })
        )
    );
    
    // Assemble card body
    cardBody.append(title, badgesContainer, moreInfoIndicator);
    
    // Assemble card
    card.append(imgContainer, cardBody);
    col.append(card);
    
    return col;
}

function displayErrorMessage() {
    const container = $('.boardgames .row');
    container.html(`
        <div class="col-12">
            <div class="alert alert-danger" role="alert">
                <h4 class="alert-heading">Error Loading Games</h4>
                <p>Unable to load board games data. Please check that the 'boardgames.json' file exists and is properly formatted.</p>
                <hr>
                <p class="mb-0">Expected JSON structure:</p>
                <pre class="mt-2 small">[
  {
    "id": 1,
    "name": "Game Name",
    "color": "#ff6b6b",
    "image": "path/to/image.jpg",
    "description": "Game description",
    "player count": "2-4",
    "notes": "Optional notes"
  }
]</pre>
            </div>
        </div>
    `);
}

// Utility function to refresh games display (useful for search functionality later)
function refreshGamesDisplay() {
    loadBoardGames();
}

// Export functions for potential use in search functionality
window.boardGamesApp = {
    refreshGamesDisplay: refreshGamesDisplay,
    loadBoardGames: loadBoardGames
};
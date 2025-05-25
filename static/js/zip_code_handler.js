// ZIP Code Handler Module
const ZipCodeHandler = {
    // Configuration
    config: {
        apiUrl: 'https://api.zippopotam.us/us/',
        minZipLength: 5,
        maxZipLength: 5,
        debounceDelay: 500, // задержка в миллисекундах для дебаунса
        maxCacheSize: 100, // максимальное количество записей в кэше
        apiTimeout: 5000 // таймаут для API запроса в миллисекундах
    },

    // Cache for storing previously fetched data
    cache: {},
    cacheKeys: [], // для отслеживания порядка добавления в кэш

    // Таймер для дебаунса
    debounceTimer: null,

    // Main function to fetch location data с дебаунсом
    fetchLocationDataDebounced(zip, callback) {
        // Очистить предыдущий таймер, если он есть
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }

        // Установить новый таймер
        this.debounceTimer = setTimeout(() => {
            this.fetchLocationData(zip).then(locationData => {
                if (typeof callback === 'function') {
                    callback(locationData);
                }
            }).catch(error => {
                console.error('Error in debounced fetch:', error);
                if (typeof callback === 'function') {
                    callback(null);
                }
            });
        }, this.config.debounceDelay);
    },

    // Основная функция для получения данных о локации
    async fetchLocationData(zip) {
        console.log('Fetching data for ZIP:', zip);

        // Validate ZIP code
        if (!this.isValidZip(zip)) {
            console.log('Invalid ZIP code format');
            return null;
        }

        // Check cache first
        if (this.cache[zip]) {
            console.log('Using cached data for ZIP:', zip);
            return this.cache[zip];
        }

        try {
            // Создаем AbortController для таймаута
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.config.apiTimeout);

            // Make API request
            const response = await fetch(`${this.config.apiUrl}${zip}`, {
                signal: controller.signal
            });
            clearTimeout(timeoutId);

            console.log('API Response status:', response.status);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('API Response data:', data);

            // Проверяем структуру ответа
            if (!data || typeof data !== 'object') {
                throw new Error('Invalid API response format');
            }

            // Проверяем, что places существует и содержит хотя бы один элемент
            if (!data.places || !Array.isArray(data.places) || data.places.length === 0) {
                console.warn('No places data found for ZIP:', zip);
                return null;
            }

            // Проверяем наличие необходимых полей
            const place = data.places[0];
            if (!place['place name'] || !place['state abbreviation']) {
                throw new Error('Missing required fields in API response');
            }

            // Extract relevant data
            const locationData = {
                city: place['place name'],
                state: place['state abbreviation']
            };

            // Store in cache
            this.addToCache(zip, locationData);
            console.log('Cached data for ZIP:', zip);

            return locationData;

        } catch (error) {
            if (error.name === 'AbortError') {
                console.error('API request timeout');
            } else if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
                console.error('Network error - API might be unavailable');
            } else {
                console.error('Error fetching location data:', error);
            }
            return null;
        }
    },

    // Validate ZIP code format
    isValidZip(zip) {
        return zip &&
            typeof zip === 'string' &&
            zip.length === this.config.minZipLength &&
            /^\d+$/.test(zip);
    },

    // Add to cache with size limit
    addToCache(zip, data) {
        // Если кэш достиг максимального размера, удаляем самую старую запись
        if (this.cacheKeys.length >= this.config.maxCacheSize) {
            const oldestKey = this.cacheKeys.shift();
            delete this.cache[oldestKey];
        }

        // Добавляем новую запись
        this.cache[zip] = data;
        this.cacheKeys.push(zip);
    },

    // Clear cache
    clearCache() {
        this.cache = {};
        this.cacheKeys = [];
        console.log('Cache cleared');
    }
};

// Export for testing in console
window.ZipCodeHandler = ZipCodeHandler;
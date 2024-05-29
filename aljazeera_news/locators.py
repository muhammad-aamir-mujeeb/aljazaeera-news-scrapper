class NewsLocators:
    search_button = "class:screen-reader-text"
    search_trigger = "class:site-header__search-trigger .no-styles-button"
    search_input = "class:search-bar__input"
    search_button_after_input = "class:css-sp7gd"
    is_results_available = '//div[@class="search-summary"]'
    sort_articles = "//select[@id='search-sort-option']//option[text()='Date']"
    search_result = "//div[@class='search-result__list']/article"
    date_locator = 'screen-reader-text'
    show_more = "//button[@data-testid='show-more-button']"
    scroll_page = "window.scrollTo(0, document.body.scrollHeight);"

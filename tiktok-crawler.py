import nodriver, re, asyncio

# tiktok content url to be accessed
BASE_URL = "https://www.tiktok.com/@soloposofficial/video/7530524408612523270"

# element selectors
comment_container_selector = '.css-7whb78-DivCommentListContainer'
comment_object_wrapper_selector = '.css-13wx63w-DivCommentObjectWrapper'
comment_content_wrapper_selector = '.css-1k8xzzl-DivCommentContentWrapper'
view_more_wrapper_selector = '.css-1ohawfw-DivViewMoreRepliesWrapper'
view_more_option_selector =  '.css-1idgi02-DivViewRepliesContainer'
view_more_span_selector = 'span[class="TUXText TUXText--tiktok-sans TUXText--weight-medium"]'
reply_item_wrapper_selector = '.css-1gstnae-DivCommentItemWrapper'
total_comments_selector = '.css-1xwyks2-PCommentTitle'

async def main():
    browser = await nodriver.start()
    tab = await browser.get(BASE_URL)
    
    # waiting for the comment list to load
    print("\nSYSTEM -> wait for the comment list to be loaded")
    while True:
        comment_container = await tab.select(comment_container_selector, timeout=12)
        if comment_container:
            print("\nSYSTEM -> comment container is loaded")
            await comment_container.scroll_into_view()
            break
    
    # display total comments
    total_comments = await tab.select(total_comments_selector)
    if total_comments:
        total_comments_text = total_comments.text
        total_comments_num = total_comments_text.split(' ')[0]
        print(f'\nSYSTEM -> there are {total_comments_num} comments to be scraped!')
    
    # wait for the page to stabilize
    await tab.wait(5)
    
    # load the comment by scrolling
    comment_object_count = 0
    scroll_attempts = 1
    while True:
        print(f"\nSYSTEM -> scroll the page to load comments, attempt: {scroll_attempts}")
        comment_object_wrapper = await tab.select_all(comment_object_wrapper_selector)
        print(f"\nSYSTEM -> {len(comment_object_wrapper)} comments loaded")
        if len(comment_object_wrapper) == comment_object_count:
            print("\nSYSTEM -> no new comments loaded, stopping scroll")
            break
        comment_object_count = len(comment_object_wrapper)
        scroll_attempts += 1
        await tab.scroll_down(75)
        print("\nSYSTEM -> waiting for new comments to load")
        await tab.wait(5)
        
    # load all replies from each comments by clicking the view replies button
    for idx ,comment in enumerate(comment_object_wrapper):
        try:
            print(f"\nSYSTEM -> processing comment number {idx+1}...")
            
            # inital checking 
            view_more_wrapper = await comment.query_selector_all(view_more_wrapper_selector)
            
            # continue to the next comment if the processed comment does not has any replies
            if not view_more_wrapper:
                print(f"\nSYSTEM -> comment number {idx+1} doesn't has any replies\nto the next comments")
                await tab.wait(4)
                continue
            
            max_tries = False
            while not max_tries:
                # logic to break the while loop, and continue to the next comment
                if max_tries:
                    break
                
                # get the view replies button 
                view_more_option = await comment.query_selector_all(view_more_option_selector)
                # get the button based on the innerText of the element
                for option in view_more_option:
                    span_el = await option.query_selector(view_more_span_selector)
                    span_el_text = span_el.text
                    if "View" in span_el_text:
                        view_replies_button = option
                    elif "Hide" in span_el_text:
                        print("SYSTEM -> button contain hide only, breaking the loop!")
                        break
                
                # process what to do next if there is/none view reply button
                if not view_replies_button:
                    print("\nSYSTEM -> no view replies buttons found...")
                    break
                else:
                    print("\nSYSTEM -> view reply button found! processing it")
                    await tab.wait(2)
                    await view_replies_button.scroll_into_view()
                    await tab.wait(4)
                    print("\nSYSTEM -> clicking the view replies button...")
                    await view_replies_button.click()
                    print("\nSYSTEM -> clicked...")
                    old_replies_count = len(await tab.select_all(reply_item_wrapper_selector))
                    for i in range(10): # 10 max retries if there is no other replies, continue to the next comment 
                        await tab.wait(6)
                        current_replies_count = len(await tab.select_all(reply_item_wrapper_selector))
                        if current_replies_count > old_replies_count:
                            print(f"\nSYSTEM -> found {current_replies_count} replies")
                            await tab.wait(4)
                            break
                        else:
                            print(f"\nSYSTEM -> replies is not loaded yet...")
                            await tab.wait(6) # wait for 3 seconds
                        # break the loop if there is no other replies to load
                        if i == 9:
                            max_tries = True
        except Exception as e:
            print(f"\nERROR -> got error on processing view replies buttons on comment number {idx+1}: {e}")
    
    # done processing the view replies buttons
    print(f"\nSYSTEM -> done processing 'view replies' buttons!✅")
    
    # scrolling the page just to make sure
    await tab.wait(4)
    await tab.scroll_up(75)
    await tab.wait(4)
    await tab.scroll_down(25)
    await tab.wait(4)
    await tab.scroll_down(50)
    await tab.wait(4)
    await tab.scroll_down(75)
    await tab.wait(4)
    await tab.scroll_down(100)
    await tab.wait(4)
    
    # proofing
    comment_content_wrapper_count = len(await tab.select_all(comment_content_wrapper_selector))
    if comment_content_wrapper_count == total_comments_num:
        print("\nSYSTEM -> successfully get all the comments and replies✅")
    else:
        print(f"\nSYSTEM -> found {comment_content_wrapper_count} / {total_comments_num}\nsomething is wrong, \nthe clicked manage to get them all tho...")
        
    
    print("\nSYSTEM -> take a screenshot of the tab")
    await tab.save_screenshot("./screenshots/ss-explore.png", format='png', full_page=True)
    print("\nSYSTEM -> screenshot saved as ./screenshots/ss-explore.png")

    # closing the browser
    print("\nSYSTEM -> close the browser")
    await tab.close()

if __name__ == "__main__":
    asyncio.run(main())
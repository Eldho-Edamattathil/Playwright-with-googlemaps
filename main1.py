from playwright.async_api import async_playwright  # Import async_playwright instead of sync_playwright
from dataclasses import dataclass, asdict, field
import pandas as pd
import argparse

@dataclass
class Business:
    """holds business data"""

    name: str = None
    address: str = None
    website: str = None
    phone_number: str = None
    
@dataclass
class BusinessList:
    """holds list of Business objects,
    and save to both excel and csv
    """
    
    business_list: list[Business] = field(default_factory=list)
    
    def dataframe(self):
        
        return pd.json_normalize(
            (asdict(business) for business in self.business_list), sep="_"
        )
    
    def save_to_excel(self, filename):
        
        self.dataframe().to_excel(f"{filename}.xlsx", index=False)

    def save_to_csv(self, filename):
        
        self.dataframe().to_csv(f"{filename}.csv", index=False)
        

async def main():  
    async with async_playwright() as p:  
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        await page.goto("https://www.google.com/maps", timeout=60000)
        await page.wait_for_timeout(5000)
        
        await page.locator('//input[@id="searchboxinput"]').fill(search_for)
        await page.wait_for_timeout(3000)

        await page.keyboard.press("Enter")
        await page.wait_for_timeout(5000)
        
        listings = await page.locator('//div[contains(@class, "Nv2PK THOPZb CpccDe ")]').all()
        business_list = BusinessList()
        
        for listing in listings:
            await listing.click()
            await page.wait_for_timeout(5000)
            
            name_xpath = '//h2[contains(@class, "bwoZTb")]/span'
            
            # name_attibute = 'aria-label'
            address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
            website_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
            phone_number_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'
            
            business = Business()
            
            if await page.locator(name_xpath).count() > 0:

                
                business.name = await page.locator(name_xpath).inner_text()
            else:
                business.name='sample'
            # business.name = listing.get_attribute(name_attibute)
            
            if await page.locator(address_xpath).count() > 0:

                
                business.address = await page.locator(address_xpath).inner_text()
            else:
                business.address='sample'
            
            if await page.locator(website_xpath).count() > 0:
                
                business.website = await page.locator(website_xpath).inner_text()
            else:
                business.website='sample'
                
            if await page.locator(phone_number_xpath).count() > 0:
                
                business.phone_number = await page.locator(phone_number_xpath).inner_text()
            else:
                business.phone_number='sample'
            
            
            
            
            # Check if any of the data is empty
            if not all([ business.address, business.website, business.phone_number]):
                print("Warning: Incomplete business data found.")
                continue
            
            business_list.business_list.append(business)
        
        # Verify if business_list has data
        print("Business List:", business_list.business_list)
        
        # Save to Excel and CSV files
        business_list.save_to_excel('google_map_data')
        business_list.save_to_csv('google_map_data')

        await browser.close()  # Close browser asynchronously
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--search", type=str)
    parser.add_argument("-l", "--location", type=str)
    args = parser.parse_args()
    
    if args.location and args.search:
        search_for = f'{args.search} {args.location}'
    else:
        search_for = 'hotels kochi'
    
    import asyncio
    asyncio.run(main())  # Run the main() function asynchronously

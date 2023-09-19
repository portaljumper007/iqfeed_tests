# Dynamically add IQFeed.CSharpApiClient DLL
assembly_path = r"C:\Users\encha\Downloads\iqfeed.csharpapiclient.2.7.0\lib\net461"

import sys
sys.path.append(assembly_path)

# Reference IQFeed.CSharpApiClient DLL
import clr
clr.AddReference("IQFeed.CSharpApiClient")

from IQFeed.CSharpApiClient import IQFeedLauncher

# Step 1 - Run IQConnect launcher
IQFeedLauncher.Start("513884", "99598775", "100")

# Step 2 - Use the appropriate factory to create the client
from IQFeed.CSharpApiClient.Lookup import LookupClientFactory
lookupClient = LookupClientFactory.CreateNew()

# Step 3 - Connect it
lookupClient.Connect()

# Step 4 - Make any requests you need or want! 
ticks = lookupClient.Historical.GetHistoryTickDatapoints("AAPL", 100)

for tick in ticks:
    print(tick)

print('Completed!')
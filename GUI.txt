import string
# Import Packages--------------
import tkinter as tk
from tkinter import ttk
from pymongo import MongoClient
import tkinter.messagebox as mb
from bson import ObjectId

# -------------------------------

# Connection Mongodb-------------------

client = MongoClient('localhost', 27017)
db = client.get_database('big_data')
games = db.get_collection('games')
publishers = db.get_collection('publishers')


# Publisher Window---------------------------------
def open_publisher_window():
    root_p = tk.Toplevel(root_main)
    root_p.title("Publisher Page")
    #root_p.geometry('420x500')
    root_p.state('zoomed')

    lblTitle = tk.Label(root_p, text="Publisher Page", font=("Helvetica", 16), bg="yellow", fg="#02577A")
    lblTitle.grid(row=0, column=0, padx=5, pady=5)

    # Frame--------------------------------------------------
    frame = tk.Frame(root_p, bg="#02577A", width=650)
    frame.grid(row=1, column=0)

    CRUDframe = tk.LabelFrame(frame, text="Queries", borderwidth=5)
    CRUDframe.grid(row=0, columnspan=7, padx=10, pady=10)

    # ****************************************************************
    # Functions:-------------------------------------
    def update():
        selected_index = publisher_tree.selection()
        if selected_index:
            old_name = publisher_tree.item(selected_index)["values"][1].strip()
            new_name = entPublisher.get()
            if new_name:
                publishers.update_many({"Publisher": old_name}, {"$set": {"Publisher": new_name}})
                mb.showinfo('Update', 'Data Updated Successfully', icon='info')
                clear()
                select()
            else:
                mb.showinfo('Required', 'Please Enter data to update the chosen record!', icon='warning')
        else:
            clear()
            mb.showinfo('Required', 'Please choose record to update', icon='warning')

    def clear():
        entPublisher.delete(0, tk.END)

    def delete():
        selected_index = publisher_tree.selection()
        if selected_index:
            old_id = publisher_tree.item(selected_index)["values"][0].strip()
            MsgBox = mb.askquestion('Delete Record', 'Are you sure! you want to delete selected Publish record',
                                    icon="warning")
            if MsgBox == 'yes':
                mb.showinfo("Information", "Publisher Record Deleted Successfully")
                publishers.find_one_and_delete({"_id": ObjectId(old_id)})
                clear()
                select()
        else:
            mb.showinfo('Required', 'Please choose record to delete', icon='warning')

    def insert():
        publisher_name = entPublisher.get()
        if publisher_name:
            publishers.insert_one({"Publisher": publisher_name})
            mb.showinfo('Insert', 'Publisher is inserted successfully', icon="info")
            clear()
            select()
        else:
            mb.showinfo('Required', 'Please Enter data to insert', icon='warning')

    def select():
        name = entPublisher.get()
        publisher_tree.delete(*publisher_tree.get_children())  # Clear previous data
        top5_tree.delete(*top5_tree.get_children())
        top5_tree.grid_remove()
        publisher_tree.grid(row=3, column=0, columnspan=7, rowspan=4, padx=5, pady=5, sticky="we")
        if name:
            for publisher in publishers.find({"Publisher": {"$regex": '^' + name, "$options": "i"}}):
                publisher_info = (publisher['_id'], publisher['Publisher'])
                publisher_tree.insert('', 'end', values=publisher_info)
            clear()
        else:
            for publisher in publishers.find():
                publisher_info = (publisher['_id'], publisher['Publisher'])
                publisher_tree.insert('', 'end', values=publisher_info)
            clear()

    def Top5Publishers():
        top5_tree.delete(*top5_tree.get_children())
        top5_tree.grid_remove()

        # Reconfigure the treeview to have only 2 columns
        top5_tree["columns"] = ("1", "2")
        top5_tree.heading("1", text="Publisher")
        top5_tree.heading("2", text="Count")
        top5_tree.column("1", width=200)
        top5_tree.column("2", width=50)

        pipeline = [
            {"$group": {"_id": "$PublisherId", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        result = list(games.aggregate(pipeline))
        for value in result:
            p_name = publishers.find_one({"_id": value["_id"]})["Publisher"]
            info = (p_name, value["count"])
            top5_tree.insert('', 'end', values=info)

        top5_tree.grid(row=3, column=0, columnspan=7, rowspan=4, padx=5, pady=5, sticky="we")

    def PublisherPlatform():
        top5_tree.delete(*top5_tree.get_children())
        top5_tree.grid_remove()
        top5_tree["columns"] = ("1")
        top5_tree.heading("1", text="Platforms ")
        top5_tree.grid(row=3, column=0, columnspan=7, rowspan=4, padx=5, pady=5, sticky="we")


        Publisher_selection = publisher_tree.selection()
        Pid = publisher_tree.item(Publisher_selection)["values"][0]

        distinct_platforms = games.distinct("Platform", {"PublisherId": ObjectId(Pid)})

        for distinct_platform in distinct_platforms:
            platform =  distinct_platform
            top5_tree.insert('', 'end', values=(platform))

    def PublisherGames():
        top5_tree.delete(*top5_tree.get_children())
        top5_tree.grid_remove()

        # Reconfigure the treeview to have 3 columns
        top5_tree["columns"] = ("1", "2", "3")
        top5_tree.heading("1", text="Games")
        top5_tree.heading("2", text="Year")
        top5_tree.heading("3", text="Genre")
        top5_tree.column("1", width=250)
        top5_tree.column("2", width=70)
        top5_tree.column("3", width=100)

        top5_tree.grid(row=3, column=0, columnspan=7, rowspan=4, padx=5, pady=5, sticky="we")

        Publishername = entPublisher.get()
        Publisher_selection = publisher_tree.selection()

        if Publishername and not Publisher_selection:
            PublisherId = publishers.find_one({"Publisher": Publishername})
            if PublisherId:
                p_games = list(games.find({"PublisherId": ObjectId(PublisherId["_id"])},
                                          {"Name": 1, "Year": 1, "Genre": 1, "_id": 0}))
                for g in p_games:
                    top5_tree.insert('', 'end', values=(g['Name'], g['Year'], g['Genre']))
                clear()
            else:
                mb.showinfo('Not Found', 'No publisher found with that name', icon='warning')
        elif Publisher_selection:
            Pid = publisher_tree.item(Publisher_selection)["values"][0]
            Publishername = publisher_tree.item(Publisher_selection)["values"][1]
            PublisherId = publishers.find_one({"_id": ObjectId(Pid)})
            if PublisherId:
                p_games = list(games.find({"PublisherId": ObjectId(PublisherId["_id"])},
                                          {"Name": 1, "Year": 1, "Genre": 1, "_id": 0}))
                for g in p_games:
                    top5_tree.insert('', 'end', values=(g['Name'], g['Year'], g['Genre']))
                clear()

    def GetNumberOfGamesForPublisherBA2000():
        top5_tree.delete(*top5_tree.get_children())
        top5_tree.grid_remove()
        top5_tree["columns"] = ("1", "2")
        top5_tree.heading("1", text="Before")
        top5_tree.heading("2", text="After")
        top5_tree.grid(row=3, column=0, columnspan=7, rowspan=4, padx=5, pady=5, sticky="we")


        Publishername = entPublisher.get()
        Publisher_selection = publisher_tree.selection()

        if Publishername and not Publisher_selection:
            PublisherId = publishers.find_one({"Publisher": Publishername})
            if PublisherId:
                PublisherId = PublisherId['_id']
                if entyear.get():
                    year = int(entyear.get())
                    B = len(list(games.find({"PublisherId": ObjectId(PublisherId["_id"]), "Year": {"$lt": year}})))
                    A = len(list(games.find({"PublisherId": ObjectId(PublisherId["_id"]), "Year": {"$gte": year}})))
                    info = (B, A)
                    top5_tree.insert('', 'end', values=info)
                    clear()
                else:
                    mb.showinfo("Year", 'Please enter Year!', icon="warning")
            else:
                mb.showinfo('Not Found', 'No publisher found with that name', icon='warning')
        elif Publisher_selection:
            Pid = publisher_tree.item(Publisher_selection)["values"][0]
            if entyear.get():
                year = int(entyear.get())
                B = len(list(games.find({"PublisherId": ObjectId(Pid), "Year": {"$lt": year}})))
                A = len(list(games.find({"PublisherId": ObjectId(Pid), "Year": {"$gte": year}})))
                info = (B, A)
                top5_tree.insert('', 'end', values=info)
                clear()
            else:
                mb.showinfo("Year", 'Please enter Year!', icon="warning")
        else:
            mb.showinfo("Publisher", "Please Enter Publisher name or select one!", icon="warning")

    # Buttons-------------------------------------------------

    update_button = tk.Button(CRUDframe, command=update, text="Update", borderwidth=5, width=10, fg="white",
                              bg="#196E78",
                              activebackground="blue", activeforeground="white")
    delete_button = tk.Button(CRUDframe, command=delete, text="Delete", borderwidth=5, width=10, fg="white",
                              bg="#196E78",
                              activebackground="red", activeforeground="white")
    insert_button = tk.Button(CRUDframe, command=insert, text="Insert", borderwidth=5, width=10, fg="white",
                              bg="#196E78",
                              activebackground="yellow", activeforeground="black")
    select_button = tk.Button(CRUDframe, command=select, text="Select", borderwidth=5, width=10, fg="white",
                              bg="#196E78",
                              activebackground="green", activeforeground="white")
    top5_button = tk.Button(CRUDframe, command=Top5Publishers, text="Top 5 Publish", borderwidth=5, width=10,
                            fg="white", bg="#196E78",
                            activebackground="green", activeforeground="white")
    publisherGames_button = tk.Button(CRUDframe, command=PublisherGames, text="Publisher Games", borderwidth=5,
                                      width=15, fg="white", bg="#196E78",
                                      activebackground="green", activeforeground="white")
    NumberOfGamesForPublisherBA2000_button = tk.Button(CRUDframe, command=GetNumberOfGamesForPublisherBA2000,
                                                       text="GamesCountBefore&After", borderwidth=5,
                                                       width=25, fg="white", bg="#196E78", activebackground="green",
                                                       activeforeground="white")

    PublisherPlatform = tk.Button(CRUDframe, command=PublisherPlatform,
                                  text="Publisher Platforms", borderwidth=5,
                                  width=25, fg="white", bg="#196E78", activebackground="green",
                                  activeforeground="white")
    # Buttons Grid--------------------------------------
    update_button.grid(row=0, column=0, padx=5, pady=5)
    delete_button.grid(row=0, column=1, padx=5, pady=5)
    insert_button.grid(row=0, column=2, padx=5, pady=5)
    select_button.grid(row=0, column=3, padx=5, pady=5)
    top5_button.grid(row=0, column=4, padx=5, pady=5)
    publisherGames_button.grid(row=0, column=5, padx=5, pady=5)
    NumberOfGamesForPublisherBA2000_button.grid(row=0, column=6, padx=5, pady=5)
    PublisherPlatform.grid(row=0, column=7, padx=5, pady=5)
    # Data Entry---------------------------
    lblPublisher = tk.Label(frame, text="Publisher", bg="white")
    lblPublisher.grid(row=1, column=0, padx=10, pady=5, sticky="nsw")
    entPublisher = tk.Entry(frame, bg="white")
    entPublisher.grid(row=1, column=0, sticky="nse")

    lblyear = tk.Label(frame, text="Year", bg="white")
    lblyear.grid(row=1, column=1, padx=10, pady=5, sticky="nsw")

    entyear = tk.Entry(frame, bg="white")
    entyear.grid(row=1, column=1, sticky="nse")

    # Select List_Box---------------------------------
    publisher_tree = ttk.Treeview(frame, columns=("ID", "Publisher"), show="headings")
    publisher_tree.heading("ID", text="ID")
    publisher_tree.heading("Publisher", text="Publisher")
    publisher_tree.grid(row=3, column=0, columnspan=7, rowspan=4, padx=5, pady=5, sticky="we")

    # Top 5 Publishers Display box--------------------
    top5_tree = ttk.Treeview(frame, columns=("1", "2", "3", "4"), show="headings")
    top5_tree.heading("1", text="Name")
    top5_tree.heading("2", text="Games Count")

    root_p.mainloop()


# Game Window-------------------------------------------
def open_game_window():
    root_m = tk.Toplevel(root_main)
    root_m.title("Game Page")
    root_m.state('zoomed')

    lblTitle = tk.Label(root_m, text="Game Page", font=("Helvetica", 16), bg="yellow", fg="#02577A")
    lblTitle.grid(row=0, column=0, padx=5, pady=5)

    # Frame--------------------------------------------------
    frame = tk.Frame(root_m, bg="#02577A", width=650)
    frame.grid(row=1, column=0)

    CRUDframe = tk.LabelFrame(frame, text="Queries", borderwidth=5)
    CRUDframe.grid(row=0, column=0, columnspan=6, padx=10, pady=10, sticky="we")

    # ****************************************************************
    # Functions:-------------------------------------

    def update():
        selected_index = games_tree.selection()
        if selected_index:
            old_id = games_tree.item(selected_index)["values"][0].strip()
            new_name = entGame.get()
            new_platform = entPlatform.get()
            new_year = int(entYear.get()) if entYear.get().isdigit() else 0
            new_genre = entGenre.get()
            new_pid = entPId.get()
            new_global = entGlobal.get()
            new_JP = entJP.get()
            new_EU = entEU.get()
            new_Other = entOther.get()
            new_NA = entNA.get()
            if new_name or new_pid or new_genre or new_platform or new_year or new_global or new_NA or new_EU or new_JP or new_Other:
                if new_name:
                    games.find_one_and_update({"_id": ObjectId(old_id)}, {"$set": {"Name": new_name}})
                if new_platform:
                    games.find_one_and_update({"_id": ObjectId(old_id)}, {"$set": {"Platform": new_platform}})
                if new_year:
                    games.find_one_and_update({"_id": ObjectId(old_id)}, {"$set": {"Year": new_year}})
                if new_genre:
                    games.find_one_and_update({"_id": ObjectId(old_id)}, {"$set": {"Genre": new_genre}})
                if new_pid:
                    games.find_one_and_update({"_id": ObjectId(old_id)}, {"$set": {"PublisherId": ObjectId(new_pid)}})
                if new_global:
                    games.find_one_and_update({"_id": ObjectId(old_id)},
                                              {"$set": {"Sales.Global_Sales": float(new_global)}})
                if new_JP:
                    games.find_one_and_update({"_id": ObjectId(old_id)}, {"$set": {"Sales.JP_Sales": float(new_JP)}})
                if new_EU:
                    games.find_one_and_update({"_id": ObjectId(old_id)}, {"$set": {"Sales.EU_Sales": float(new_EU)}})
                if new_Other:
                    games.find_one_and_update({"_id": ObjectId(old_id)},
                                              {"$set": {"Sales.Other_Sales": float(new_Other)}})
                if new_NA:
                    games.find_one_and_update({'_id': ObjectId(old_id)}, {"$set": {"Sales.NA_Sales": float(new_NA)}})
                mb.showinfo('Update', 'Data Updated Successfully', icon='info')
                clear()
                select()
            else:
                mb.showinfo('Required', 'Please Enter data to update the chosen record!', icon='warning')
        else:
            clear()
            mb.showinfo('Required', 'Please choose record to update', icon='warning')

    def clear():
        entGame.delete(0, tk.END)
        entGenre.delete(0, tk.END)
        entYear.delete(0, tk.END)
        entPlatform.delete(0, tk.END)
        entPId.delete(0, tk.END)
        entGlobal.delete(0, tk.END)
        entNA.delete(0, tk.END)
        entEU.delete(0, tk.END)
        entJP.delete(0, tk.END)
        entOther.delete(0, tk.END)

    def delete():

        selected_index = games_tree.selection()
        if selected_index:
            old_id = games_tree.item(selected_index)["values"][0].strip()
            MsgBox = mb.askquestion('Delete Record', 'Are you sure! you want to delete selected Publish record',
                                    icon="warning")
            if MsgBox == 'yes':
                mb.showinfo("Information", "Publisher Record Deleted Successfully")
                games.find_one_and_delete({"_id": ObjectId(old_id)})
                clear()
                select()
        else:
            mb.showinfo('Required', 'Please choose record to delete', icon='warning')

    def insert():
        game_name = entGame.get()
        game_platform = entPlatform.get()
        game_year = int(entYear.get()) if entYear.get().isdigit() else 0
        game_genre = entGenre.get()
        game_publisherId = (entPId.get())
        game_global = entGlobal.get()
        game_NA = entNA.get()
        game_EU = entEU.get()
        game_JP = entJP.get()
        game_Other = entOther.get()
        if game_name and game_platform and game_year and game_genre and game_publisherId and game_Other and game_JP and game_EU and game_NA and game_global:
            sales = {
                "Global_Sales": float(game_global),
                "JP_Sales": float(game_JP),
                "EU_Sales": float(game_EU),
                "Other_Sales": float(game_Other),
                "NA_Sales": float(game_NA)
            }
            games.insert_one({"Name": game_name, "Platform": game_platform, "Year": game_year, "Genre": game_genre,
                              "PublisherId": ObjectId(game_publisherId), "Sales": sales})
            mb.showinfo('Insert', 'Game is inserted successfully', icon="info")
            clear()
            select()
        else:
            mb.showinfo('Required', 'Please Enter data to insert', icon='warning')

    def select():

        games_tree.delete(*games_tree.get_children())
        games_tree.column("1", width=200)
        games_tree.column("2", width=200)
        games_tree.column("3", width=100)
        games_tree.column("4", width=100)
        games_tree.column("5", width=100)
        games_tree.column("6", width=200)
        games_tree.column("7", width=100)
        games_tree.column("8", width=100)
        games_tree.column("9", width=100)
        games_tree.column("10", width=100)
        games_tree.column("11", width=100)



        # Handle Headers
        games_tree.heading("1", text="ID")
        games_tree.heading("2", text="Name")
        games_tree.heading("3", text="Platform")
        games_tree.heading("4", text="Year")
        games_tree.heading("5", text="Genre")
        games_tree.heading("6", text="PublisherId")
        games_tree.heading("7", text="Global")
        games_tree.heading("8", text="JP")
        games_tree.heading("9", text="EU")
        games_tree.heading("10", text="NA")
        games_tree.heading("11", text="OtherSales")

        new_name = entGame.get()
        new_platform = entPlatform.get()
        new_year = int(entYear.get()) if entYear.get().isdigit() else 0
        new_genre = entGenre.get()
        new_pid = entPId.get()

        if new_name or new_platform or new_year or new_pid or new_genre:
            clear()
            if new_name:
                for game in games.find({"Name": {"$regex": '^' + new_name, "$options": "i"}}):
                    game_info = (
                        game['_id'], game['Name'], game['Platform'], game['Year'], game['Genre'], game['PublisherId'],
                        game['Sales']['Global_Sales'], game['Sales']['JP_Sales'],
                        game['Sales']['EU_Sales'], game['Sales']['Other_Sales'], game['Sales']['NA_Sales'])
                    games_tree.insert('', 'end', values=game_info)
            if new_platform:
                for game in games.find({"Platform": {"$regex": '^' + new_platform, "$options": "i"}}):
                    game_info = (
                        game['_id'], game['Name'], game['Platform'], game['Year'], game['Genre'], game['PublisherId'],
                        game['Sales']['Global_Sales'], game['Sales']['JP_Sales'],
                        game['Sales']['EU_Sales'], game['Sales']['Other_Sales'], game['Sales']['NA_Sales'])
                    games_tree.insert('', 'end', values=game_info)

            if new_genre:
                for game in games.find({"Genre": {"$regex": '^' + new_genre, "$options": "i"}}):
                    game_info = (
                        game['_id'], game['Name'], game['Platform'], game['Year'], game['Genre'], game['PublisherId'],
                        game['Sales']['Global_Sales'], game['Sales']['JP_Sales'],
                        game['Sales']['EU_Sales'], game['Sales']['Other_Sales'], game['Sales']['NA_Sales'])
                    games_tree.insert('', 'end', values=game_info)
            if new_year:
                for game in games.find({"Year": new_year}):
                    game_info = (
                        game['_id'], game['Name'], game['Platform'], game['Year'], game['Genre'], game['PublisherId'],
                        game['Sales']['Global_Sales'], game['Sales']['JP_Sales'],
                        game['Sales']['EU_Sales'], game['Sales']['Other_Sales'], game['Sales']['NA_Sales'])
                    games_tree.insert('', 'end', values=game_info)
            if new_pid:
                for game in games.find({"PublisherId": ObjectId(new_pid)}):
                    game_info = (
                        game['_id'], game['Name'], game['Platform'], game['Year'], game['Genre'], game['PublisherId'],
                        game['Sales']['Global_Sales'], game['Sales']['JP_Sales'],
                        game['Sales']['EU_Sales'], game['Sales']['Other_Sales'], game['Sales']['NA_Sales'])
                    games_tree.insert('', 'end', values=game_info)
            # ------------------
        else:
            for game in games.find():
                game_info = (
                game['_id'], game['Name'], game['Platform'], game['Year'], game['Genre'], game['PublisherId'],
                game['Sales']['Global_Sales'], game['Sales']['JP_Sales'],
                game['Sales']['EU_Sales'], game['Sales']['Other_Sales'], game['Sales']['NA_Sales'])
                games_tree.insert('', 'end', values=game_info)


    def MaxSalesYear():
        games_tree.delete(*games_tree.get_children())
        # Determine the location based on the provided inputs
        if entGlobal.get():
            location = "Global_Sales"
        elif entJP.get():
            location = "JP_Sales"
        elif entEU.get():
            location = "EU_Sales"
        elif entOther.get():
            location = "Other_Sales"
        elif entNA.get():
            location = "NA_Sales"
        else:
            location = "Global_Sales"

        games_tree.column("1", width=200)
        games_tree.column("2", width=200)
        games_tree.column("3", width=0)
        games_tree.column("4", width=0)
        games_tree.column("5", width=0)
        games_tree.column("6", width=0)
        games_tree.column("7", width=0)
        games_tree.column("8", width=0)
        games_tree.column("9", width=0)
        games_tree.column("10", width=0)
        games_tree.column("11", width=0)

        # Handle Headers

        games_tree.heading("1", text="Year")
        games_tree.heading("2", text=f"{location}")
        games_tree.heading("3", text="")
        games_tree.heading("4", text="")
        games_tree.heading("5", text="")
        games_tree.heading("6", text="")
        games_tree.heading("7", text="")
        games_tree.heading("8", text="")
        games_tree.heading("9", text="")
        games_tree.heading("10", text="")
        games_tree.heading("11", text="")



        pipeline = [
            {"$group": {"_id": "$Year", f"{location}": {"$sum": f"$Sales.{location}"}}},
            {"$sort": {f"{location}": -1}},
            {"$limit": 1}
        ]
        result = games.aggregate(pipeline)

        for r in result:
            games_tree.insert('', 'end', values=(r['_id'], r[f'{location}']))
        clear()
    def Top5GamesSales():
        games_tree.delete(*games_tree.get_children())
        if entGlobal.get():
            location = "Global_Sales"
        elif entJP.get():
            location = "JP_Sales"
        elif entEU.get():
            location = "EU_Sales"
        elif entOther.get():
            location = "Other_Sales"
        elif entNA.get():
            location = "NA_Sales"
        else:
            location = "Global_Sales"

        result = games.find({}, {f"Sales.{location}": 1, "_id": 0, "Name": 1, "Genre": 1, "Year": 1}).sort(
            {f"Sales.{location}": -1}).limit(5)

        games_tree.column("1", width=200)
        games_tree.column("2", width=200)
        games_tree.column("3", width=100)
        games_tree.column("4", width=100)
        games_tree.column("5", width=0)
        games_tree.column("6", width=0)
        games_tree.column("7", width=0)
        games_tree.column("8", width=0)
        games_tree.column("9", width=0)
        games_tree.column("10", width=0)
        games_tree.column("11", width=0)

        # Handle Headers

        games_tree.heading("1", text="Year")
        games_tree.heading("2", text="Name")
        games_tree.heading("3", text="Genre")
        games_tree.heading("4", text=f"Sales in {location}")
        games_tree.heading("5", text="")
        games_tree.heading("6", text="")
        games_tree.heading("7", text="")
        games_tree.heading("8", text="")
        games_tree.heading("9", text="")
        games_tree.heading("10", text="")
        games_tree.heading("11", text="")


        #games_tree.grid(row=3, column=0, columnspan=6, rowspan=4, padx=5, pady=5, sticky="we")
        for r in result:
            games_tree.insert('', 'end', values=(r['Name'], r['Year'], r['Genre'], r['Sales'][location]))
        clear()
    def NumberOfViolentGamesRanges():
        games_tree.delete(*games_tree.get_children())
        if entYear.get():
            year = int(entYear.get())
            greate = len(list(games.find({"Year": {"$gte": year}, "Genre": {"$in": ["Action", "Fighting"]}})))
            less = len(list(games.find({"Year": {"$lt": year}, "Genre": {"$in": ["Action", "Fighting"]}})))
            result = {f"Count After {year}": greate, f"Count Before {year}": less}

            games_tree.column("1", width=200)
            games_tree.column("2", width=200)
            games_tree.column("3", width=0)
            games_tree.column("4", width=0)
            games_tree.column("5", width=0)
            games_tree.column("6", width=0)
            games_tree.column("7", width=0)
            games_tree.column("8", width=0)
            games_tree.column("9", width=0)
            games_tree.column("10", width=0)
            games_tree.column("11", width=0)

            # Handle Headers

            games_tree.heading("1", text=f"Violent Count Before {year}")
            games_tree.heading("2", text=f"Violent Count After {year}")
            games_tree.heading("3", text="")
            games_tree.heading("4", text="")
            games_tree.heading("5", text="")
            games_tree.heading("6", text="")
            games_tree.heading("7", text="")
            games_tree.heading("8", text="")
            games_tree.heading("9", text="")
            games_tree.heading("10", text="")
            games_tree.heading("11", text="")




            games_tree.insert('', 'end', values=(result[f'Count After {year}'], result[f'Count Before {year}']))
        else:
            mb.showinfo("Year", "Pleas Enter Year", icon="warning")
        clear()
    def MapReducePlatformSales():
        games_tree.delete(*games_tree.get_children())
        if entGlobal.get():
            location = "Global_Sales"
        elif entJP.get():
            location = "JP_Sales"
        elif entEU.get():
            location = "EU_Sales"
        elif entOther.get():
            location = "Other_Sales"
        elif entNA.get():
            location = "NA_Sales"
        else:
            location = "Global_Sales"

        games_tree.column("1", width=200)
        games_tree.column("2", width=200)
        games_tree.column("3", width=0)
        games_tree.column("4", width=0)
        games_tree.column("5", width=0)
        games_tree.column("6", width=0)
        games_tree.column("7", width=0)
        games_tree.column("8", width=0)
        games_tree.column("9", width=0)
        games_tree.column("10", width=0)
        games_tree.column("11", width=0)

        # Handle Headers

        games_tree.heading("1", text="Platform")
        games_tree.heading("2", text=f"total Sales {location}")
        games_tree.heading("3", text="")
        games_tree.heading("4", text="")
        games_tree.heading("5", text="")
        games_tree.heading("6", text="")
        games_tree.heading("7", text="")
        games_tree.heading("8", text="")
        games_tree.heading("9", text="")
        games_tree.heading("10", text="")
        games_tree.heading("11", text="")


        result = db.games.aggregate([
            {"$match": {"Sales": {"$exists": True, "$ne": None}}},
            {"$project": {"Platform": 1, "Sales": 1}},
            {"$group": {"_id": "$Platform", "totalSales": {"$sum": "$Sales." + location}}},
            {"$sort": {"totalSales": -1}}  # Sort by totalSales in descending order
        ])
        for r in result:
            games_tree.insert('', 'end', values=(r['_id'], r['totalSales']))
        clear()
    def MAXreleasedGenre():
        games_tree.delete(*games_tree.get_children())
        games_tree.column("1", width=200)
        games_tree.column("2", width=200)
        games_tree.column("3", width=0)
        games_tree.column("4", width=0)
        games_tree.column("5", width=0)
        games_tree.column("6", width=0)
        games_tree.column("7", width=0)
        games_tree.column("8", width=0)
        games_tree.column("9", width=0)
        games_tree.column("10", width=0)
        games_tree.column("11", width=0)

        # Handle Headers

        games_tree.heading("1", text="Genre")
        games_tree.heading("2", text="Number Of Games")
        games_tree.heading("3", text="")
        games_tree.heading("4", text="")
        games_tree.heading("5", text="")
        games_tree.heading("6", text="")
        games_tree.heading("7", text="")
        games_tree.heading("8", text="")
        games_tree.heading("9", text="")
        games_tree.heading("10", text="")
        games_tree.heading("11", text="")

        pipeline = [
            {"$group": {"_id": "$Genre", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 1}
        ]
        result = list(games.aggregate(pipeline))

        games_tree.insert('', 'end', values=(result[0]['_id'], result[0]['count']))
        clear()
    def MAXreleasedYear():
        games_tree.delete(*games_tree.get_children())
        games_tree.column("1", width=200)
        games_tree.column("2", width=200)
        games_tree.column("3", width=0)
        games_tree.column("4", width=0)
        games_tree.column("5", width=0)
        games_tree.column("6", width=0)
        games_tree.column("7", width=0)
        games_tree.column("8", width=0)
        games_tree.column("9", width=0)
        games_tree.column("10", width=0)
        games_tree.column("11", width=0)

        # Handle Headers

        games_tree.heading("1", text="Year")
        games_tree.heading("2", text="Number Of Games ")
        games_tree.heading("3", text="")
        games_tree.heading("4", text="")
        games_tree.heading("5", text="")
        games_tree.heading("6", text="")
        games_tree.heading("7", text="")
        games_tree.heading("8", text="")
        games_tree.heading("9", text="")
        games_tree.heading("10", text="")
        games_tree.heading("11", text="")

        pipeline = [
            {"$group": {"_id": "$Year", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 1}
        ]
        result = list(games.aggregate(pipeline))

        games_tree.insert('', 'end', values=(result[0]['_id'], result[0]['count']))
        clear()
    def Top5platforms():
        games_tree.delete(*games_tree.get_children())
        games_tree.column("1", width=200)
        games_tree.column("2", width=200)
        games_tree.column("3", width=0)
        games_tree.column("4", width=0)
        games_tree.column("5", width=0)
        games_tree.column("6", width=0)
        games_tree.column("7", width=0)
        games_tree.column("8", width=0)
        games_tree.column("9", width=0)
        games_tree.column("10", width=0)
        games_tree.column("11", width=0)

        # Handle Headers

        games_tree.heading("1", text="Platform")
        games_tree.heading("2", text="Number Of Games ")
        games_tree.heading("3", text="")
        games_tree.heading("4", text="")
        games_tree.heading("5", text="")
        games_tree.heading("6", text="")
        games_tree.heading("7", text="")
        games_tree.heading("8", text="")
        games_tree.heading("9", text="")
        games_tree.heading("10", text="")
        games_tree.heading("11", text="")


        pipeline = [
            {"$group": {"_id": "$Platform", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        result = list(games.aggregate(pipeline))
        for r in result:
            games_tree.insert('', 'end', values=(r['_id'], r['count']))
        clear()
    # Buttons-------------------------------------------------

    update_button = tk.Button(CRUDframe, command=update, text="Update", borderwidth=5, width=10, fg="white",
                              bg="#196E78",
                              activebackground="blue", activeforeground="white")
    delete_button = tk.Button(CRUDframe, command=delete, text="Delete", borderwidth=5, width=10, fg="white",
                              bg="#196E78",
                              activebackground="red", activeforeground="white")
    insert_button = tk.Button(CRUDframe, command=insert, text="Insert", borderwidth=5, width=10, fg="white",
                              bg="#196E78",
                              activebackground="yellow", activeforeground="black")
    select_button = tk.Button(CRUDframe, command=select, text="Select", borderwidth=5, width=10, fg="white",
                              bg="#196E78",
                              activebackground="green", activeforeground="white")

    Max_Sales_Year = tk.Button(CRUDframe, command=MaxSalesYear, text="Max Sales Year", borderwidth=5, width=15,
                               fg="white",
                               bg="#196E78",
                               activebackground="green", activeforeground="white")
    Top_5Games = tk.Button(CRUDframe, command=Top5GamesSales, text="Top 5 Games in !", borderwidth=5, width=15,
                           fg="white",
                           bg="#196E78",
                           activebackground="green", activeforeground="white")

    Map_Reduce_Platform_Sales = tk.Button(CRUDframe, command=MapReducePlatformSales, text="Map Reduce Platform_Sales",
                                          borderwidth=5, width=25,
                                          fg="white",
                                          bg="#196E78",
                                          activebackground="green", activeforeground="white")

    NumberOfViolentGamesRanges = tk.Button(CRUDframe, command=NumberOfViolentGamesRanges, text="Violent Games in ",
                                           borderwidth=5, width=20,
                                           fg="white",
                                           bg="#196E78",
                                           activebackground="green", activeforeground="white")
    MAXreleasedGenre = tk.Button(CRUDframe, command=MAXreleasedGenre, text="Top Genre ",
                                 borderwidth=5, width=14,
                                 fg="white",
                                 bg="#196E78",
                                 activebackground="green", activeforeground="white")
    MAXreleasedYear = tk.Button(CRUDframe, command=MAXreleasedYear, text="Top Year ",
                                borderwidth=5, width=14,
                                fg="white",
                                bg="#196E78",
                                activebackground="green", activeforeground="white")

    Top5platformsB = tk.Button(CRUDframe, command=Top5platforms, text="Top 5 Platforms",
                               borderwidth=5, width=14,
                               fg="white",
                               bg="#196E78",
                               activebackground="green", activeforeground="white")
    update_button.grid(row=0, column=0, padx=5, pady=5)
    delete_button.grid(row=0, column=1, padx=5, pady=5)
    insert_button.grid(row=0, column=2, padx=5, pady=5)
    select_button.grid(row=0, column=3, padx=5, pady=5)
    Max_Sales_Year.grid(row=0, column=4, padx=5, pady=5)
    Map_Reduce_Platform_Sales.grid(row=0, column=6, padx=5, pady=5)
    Top_5Games.grid(row=0, column=7, padx=5, pady=5)
    NumberOfViolentGamesRanges.grid(row=0, column=8, padx=5, pady=5)
    MAXreleasedYear.grid(row=0, column=9, padx=5, pady=5)
    MAXreleasedGenre.grid(row=0, column=10, padx=5, pady=5)
    Top5platformsB.grid(row=0, column=11, padx=5, pady=5)
    # Data Entry---------------------------
    lblGame = tk.Label(frame, text="Name", bg="white")
    lblGame.grid(row=1, column=0, padx=5, pady=5, sticky="nsw")

    entGame = tk.Entry(frame, bg="white")
    entGame.grid(row=1, column=0, sticky="nse")

    lblPlatform = tk.Label(frame, text="Platform", bg="white")
    lblPlatform.grid(row=1, column=1, padx=10, pady=5, sticky="nsw")

    entPlatform = tk.Entry(frame, bg="white")
    entPlatform.grid(row=1, column=1, sticky="nse")

    lblYear = tk.Label(frame, text="Year", bg="white")
    lblYear.grid(row=1, column=2, padx=5, pady=5, sticky="nsw")

    entYear = tk.Entry(frame, bg="white")
    entYear.grid(row=1, column=2, sticky="nse")

    lblGenre = tk.Label(frame, text="Genre", bg="white")
    lblGenre.grid(row=1, column=3, padx=5, pady=5, sticky="nsw")

    entGenre = tk.Entry(frame, bg="white")
    entGenre.grid(row=1, column=3, sticky="nse")

    lblGame = tk.Label(frame, text="Name", bg="white")
    lblGame.grid(row=1, column=0, padx=5, pady=5, sticky="nsw")

    entGame = tk.Entry(frame, bg="white")
    entGame.grid(row=1, column=0, sticky="nse")

    lblPlatform = tk.Label(frame, text="Platform", bg="white")
    lblPlatform.grid(row=1, column=1, padx=10, pady=5, sticky="nsw")

    entPlatform = tk.Entry(frame, bg="white")
    entPlatform.grid(row=1, column=1, sticky="nse")

    lblYear = tk.Label(frame, text="Year", bg="white")
    lblYear.grid(row=1, column=2, padx=5, pady=5, sticky="nsw")

    entYear = tk.Entry(frame, bg="white")
    entYear.grid(row=1, column=2, sticky="nse")

    lblGenre = tk.Label(frame, text="Genre", bg="white")
    lblGenre.grid(row=1, column=3, padx=5, pady=5, sticky="nsw")

    entGenre = tk.Entry(frame, bg="white")
    entGenre.grid(row=1, column=3, sticky="nse")

    lblPId = tk.Label(frame, text="PublisherId", bg="white")
    lblPId.grid(row=1, column=4, padx=5, pady=5, sticky="nsw")

    entPId = tk.Entry(frame, bg="white")
    entPId.grid(row=1, column=4, sticky="nse")

    # "Global_Sales": 82.74,
    lblGlobal = tk.Label(frame, text="Global_Sales", bg="white")
    lblGlobal.grid(row=2, column=0, padx=5, pady=5, sticky="nsw")

    entGlobal = tk.Entry(frame, bg="white")
    entGlobal.grid(row=2, column=0, sticky="nse")

    # "JP_Sales": 3.77,
    lblJP = tk.Label(frame, text="JP_Sales", bg="white")
    lblJP.grid(row=2, column=1, padx=5, pady=5, sticky="nsw")

    entJP = tk.Entry(frame, bg="white")
    entJP.grid(row=2, column=1, sticky="nse")

    # "EU_Sales": 29.02,
    lblEU = tk.Label(frame, text="EU_Sales", bg="white")
    lblEU.grid(row=2, column=2, padx=5, pady=5, sticky="nsw")

    entEU = tk.Entry(frame, bg="white")
    entEU.grid(row=2, column=2, sticky="nse")

    # "NA_Sales": 41.49
    lblNA = tk.Label(frame, text="NA_Sales", bg="white")
    lblNA.grid(row=2, column=3, padx=5, pady=5, sticky="nsw")

    entNA = tk.Entry(frame, bg="white")
    entNA.grid(row=2, column=3, sticky="nse")

    # "Other_Sales": 8.46,
    lblOther = tk.Label(frame, text="Other_Sales", bg="white")
    lblOther.grid(row=2, column=4, padx=5, pady=5, sticky="nsw")

    entOther = tk.Entry(frame, bg="white")
    entOther.grid(row=2, column=4, sticky="nse")

    # Select List_Box---------------------------------
    # Select List_Box---------------------------------
    games_tree = ttk.Treeview(frame, columns=("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"), show="headings")
    # Handle Columns
    games_tree.column("1", width=200)
    games_tree.column("2", width=200)
    games_tree.column("3", width=100)
    games_tree.column("4", width=100)
    games_tree.column("5", width=100)
    games_tree.column("6", width=200)
    games_tree.column("7", width=100)
    games_tree.column("8", width=100)
    games_tree.column("9", width=100)
    games_tree.column("10", width=100)
    games_tree.column("11", width=100)

    # Handle Headers
    games_tree.heading("1", text="ID")
    games_tree.heading("2", text="Name")
    games_tree.heading("3", text="Platform")
    games_tree.heading("4", text="Year")
    games_tree.heading("5", text="Genre")
    games_tree.heading("6", text="PublisherId")
    games_tree.heading("7", text="Global")
    games_tree.heading("8", text="JP")
    games_tree.heading("9", text="EU")
    games_tree.heading("10", text="NA")
    games_tree.heading("11", text="OtherSales")
    games_tree.grid(row=3, column=0, columnspan=6, rowspan=4, padx=5, pady=5, sticky="we")

    root_m.grid_columnconfigure(0, weight=1)
    root_m.grid_columnconfigure(1, weight=1)
    root_m.mainloop()


# Build Main Tkinter Window--------------------------
root_main = tk.Tk()
root_main.title("Video Games Sales")
root_main.state('zoomed')

lblTitle = tk.Label(root_main, text="Video Games Sales", font=("Helvetica", 16), bg="yellow", fg="#02577A")
lblTitle.grid(row=0, padx=5, pady=5, columnspan=4, sticky="nsew")  # Centered horizontally
# Menu_Configration---------------------------------
"""menu = tk.Menu(root_main)
root_main.config(menu=menu)

Query1menu = tk.Menu(menu)
menu.add_cascade(label='Max', menu=Query1menu)
Query1menu.add_command(label='New')
Query1menu.add_command(label='Open...')
Query1menu.add_separator()
Query1menu.add_command(label='Exit', command=root_main.quit)

Query2menu = tk.Menu(menu)
menu.add_cascade(label='Query2', menu=Query2menu)
Query2menu.add_command(label='About')"""
# Main Buttons-----------------------------------
game_window_btn = tk.Button(root_main, command=open_game_window, text="Games", borderwidth=5, width=10, fg="white",
                            bg="#196E78",
                            activebackground="green", activeforeground="white")
publisher_window_btn = tk.Button(root_main, command=open_publisher_window, text="Publisher", borderwidth=5, width=10,
                                 fg="white", bg="#196E78",
                                 activebackground="green", activeforeground="white")
game_window_btn.grid(row=1, column=0, pady=5, padx=5, sticky="nsew")
publisher_window_btn.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

# Configure column weights to center the buttons
root_main.grid_columnconfigure(0, weight=1)
root_main.grid_columnconfigure(1, weight=1)

root_main.mainloop()

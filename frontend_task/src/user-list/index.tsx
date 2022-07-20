import {useUserList} from "./use-user-list";
import Typography from '@mui/material/Typography';
import Box from "@mui/material/Box";
import { TextField } from "@mui/material";
import { useState } from "react";

type UserProps = {
    name?: string,
    lastPostTitle?: string,
    lastPostBody?: string,
}


const UserListItem = ({name, lastPostTitle, lastPostBody}: UserProps) => (
    <>
        <Typography variant="h6" mb={1}>
            {name}
        </Typography>
        <Typography variant="subtitle1" mb={1}>
            <strong>{lastPostTitle}</strong>
        </Typography>
        <Typography variant="body2" mb={5}>
            {lastPostBody}
        </Typography>
    </>
)

export const UserList = () => {
    const { userData } = useUserList();
    // bind the user search term to the state so the component reloads when it changes
    const [userFilter, setUserFilter] = useState<string>('');
    let filteredUserData;

    if(userFilter !== '') {
        // search for the lower case term in the user names
        filteredUserData = userData.filter((user) => {
            return user.name.toLowerCase().includes(userFilter)
        })
    }

    // display the filtered data if it exists, otherwise show the full list
    const dataToDisplay = filteredUserData ?? userData
    return(
        <>
            <TextField
              id="user-filter"
              label="Search user by name"
              variant='outlined'
              onChange={(e) => setUserFilter(e.target.value)}
              margin="normal"
            />
            <Box ml="100px" mt="50px" alignItems="center" style={{ width: '70%', textAlign: 'left' }}>
                {dataToDisplay.map((user) => (
                    <>
                        <UserListItem
                            name={user.name}
                            lastPostTitle={user.lastPostTitle}
                            lastPostBody={user.lastPostBody}
                        />
                    </>
                ))}
            </Box>
        </>
    )
}

import logo from './garlic.png'
import './App.css';
import React, { useState, useEffect, APIService, props } from 'react'
import axios from 'axios';

// 1. import `ChakraProvider` component
import { ChakraProvider, FormControl, HStack } from '@chakra-ui/react'
import { SimpleGrid, Heading, Text, Image, Input, Divider, Stack, Select, Checkbox } from '@chakra-ui/react'
import { Card, CardHeader, CardBody, Box, Button, CheckboxGroup } from '@chakra-ui/react'

function App() {

  //form word input
  const [input, setInput] = useState('');

  //filter checkbox inputs
  const [lyric, setLyric] = useState('');
  const [phrase, setPhrase] = useState('');
  const [urban, setUrban] = useState('');
  const [joke, setJoke] = useState('');
  const [proverb, setProverb] = useState('');
  const [quote, setQuote] = useState('');
  const [lang, setLang] = useState('');
  const [nsfw, setNSFW] = useState('');


  //receive api call from script
  const [output, setOutput] = useState('');
  const [data, setData] = useState('');

  //receive script output 
  useEffect(() => {
    fetch("/").then(
      res => res.json()
    ).then(
      data => {
        setData(data)
        console.log("data from flask " + data)
      }
    )
  })


  // function getData() {
  //   axios({
  //     method: "GET",
  //     url: "/",
  //   })
  //     .then((response) => {
  //       const res = response.data
  //       setOutput(({
  //         outputRes: res.output
  //       }))
  //     }).catch((error) => {
  //       if (error.response) {
  //         console.log(error.response)
  //         console.log(error.response.status)
  //         console.log(error.response.headers)
  //       }
  //     })
  // }
  // getData()

  // const insertArticle = () => {
  //   APIService.InsertArticle({ input })
  //     .then((response) => props.insertedArticle(response))
  //     .catch(error => console.log('error', error))
  // }

  const handleSubmit = (event) => {
    event.preventDefault()
    // getData()
    // insertArticle()
    setInput('')
    setLyric('')
    setPhrase('')
  }



  return (
    <ChakraProvider>
      <form onSubmit={(event) => handleSubmit(event)}>
        <FormControl >
          <SimpleGrid columns={2} p={20}>
            <Card variant={'outline'} borderColor={'gray'} background={'gray.50'}>
              <CardHeader >
                <HStack >
                  <Heading size='lg'> PunGenT</Heading>
                  <Image w={"50px"} h={"40px"} src={logo} />
                </HStack>
                <Text fontSize='xs'> Your one-stop-shop for wordplay!</Text>
                <HStack>
                  <Input placeholder='Your idea here!' size='md' width={'auto'} value={input}
                    onChange={(event) => setInput(event.target.value)} />
                  <Button colorScheme='blackAlpha' type='submit'> Generate</Button>
                </HStack>

              </CardHeader>
              <CardBody>
                <Box w='md' h='150px' p={4} borderWidth='2px' overflowY={'scroll'} >
                  <Text> {data.output}</Text>
                </Box>
              </CardBody>
            </Card>
            <Card variant={'outline'} borderColor={'gray'} background={'gray.50'}>
              <CardHeader>
                <Heading size='md'> Filters</Heading>
              </CardHeader>
              <CardBody>
                <Stack align={'center'} h='100px'>
                  <Divider orientation='horizontal' />
                  <HStack >
                    <CheckboxGroup colorScheme='green'>
                      <HStack>
                        <Stack spacing={[1, 5]} direction={['row', 'column']}>
                          <Checkbox
                            value='lyrics'
                            checked={lyric}
                            onChange={(e) => this.setState({ checkLyric: e.target.checked })}
                          >Lyrics</Checkbox>
                          <Checkbox value='phrases'>Phrases</Checkbox>
                          <Checkbox value='urban'>Urban</Checkbox>
                        </Stack>
                        <Stack spacing={[1, 5]} direction={['row', 'column']}  >
                          <Checkbox value='jokes'>Jokes</Checkbox>
                          <Checkbox value='proverbs'>Proverbs</Checkbox>
                          <Checkbox value='quotes'>Anime Quotes</Checkbox>
                        </Stack>
                      </HStack>
                    </CheckboxGroup>
                  </HStack>
                  <Divider orientation='horizontal' colorScheme={'blackAlpha'} />
                  <Select align='center' pl='10px' w='md' placeholder='Select Language'>
                    <option value='option1'>English</option>
                    <option value='option2'>Spanish</option>
                    <option value='option3'>French</option>
                  </Select>

                  <Checkbox colorScheme='red' value='nsfw'> Include NSFW puns</Checkbox>
                </Stack>
              </CardBody>
            </Card>
          </SimpleGrid>
        </FormControl>


      </form>

    </ChakraProvider >
  )
}


export default App;

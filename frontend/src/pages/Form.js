import React, { Component } from 'react';

export class Form extends Component {
    render() {
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
                                                <Checkbox value='lyrics'>Lyrics</Checkbox>
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
    }
}



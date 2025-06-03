import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
from gensim.models import Word2Vec
import torch
import numpy as np
from llm.SimpleNN import SimpleNN
import torch.nn.functional as F
working_directory = os.getcwd()
torch.serialization.add_safe_globals({'SimpleNN': SimpleNN})


# Load pretrained Word2Vec model for input transformation
word2vec_model = Word2Vec.load(working_directory+'/llm/word2vec.model')


def load_checkpoint(filepath):
    """Loads a pretrained model from a given checkpoint"""
    checkpoint = torch.load(filepath)
    model = SimpleNN(100, 128, 3, 6)
    model.load_state_dict(checkpoint['state_dict'])
    
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    optimizer.load_state_dict(checkpoint['optimizer'])
    
    epoch = checkpoint['epoch']
    best_loss = checkpoint['best_loss']
    
    return model, optimizer, epoch, best_loss
model, optimizer, start_epoch, best_loss = load_checkpoint(working_directory+'/llm/best_model.pth.tar')

def sentence_to_vector(sentence, model):
    """
    Vectorizes inputs using the word2vec model.
    """
    words = sentence.split()
    word_vectors = [model.wv[word] for word in words if word in model.wv]
    if len(word_vectors) == 0:
        return np.zeros(model.vector_size)
    return np.mean(word_vectors, axis=0)

def predict_emotion(sentence, device):
    """
    Predicts the emotion of the text
    """
    vec = sentence_to_vector(sentence=sentence, model=word2vec_model)
    model.to(device)
    model.eval()
    input = torch.tensor(vec).unsqueeze(0).to(device)

    with torch.no_grad():
        pred = model(input)
        probabilities = F.softmax(pred, dim=1)

        # Get the index of the highest probability
        predicted_class_idx = torch.argmax(probabilities, dim=1).item()

        # Define your label mapping
        label_mapping = {0: 'Sad', 1: 'Happy', 2: 'Love', 3: 'Angry', 4: 'Fear', 5: 'Surprised', 6: 'Neutral'}

        # Map the predicted index to the corresponding label
        predicted_label = label_mapping[predicted_class_idx]
        print(predicted_label)
    return predicted_label